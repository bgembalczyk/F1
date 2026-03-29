from __future__ import annotations

import ast
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from scrapers.base.domain_entrypoint import get_domain_entrypoint_scraper_metadata
from tests.architecture.registry import ARCHITECTURE_REGISTRY
from tests.architecture.rules import ENTRYPOINT_MODULES


def _entrypoint_module_paths() -> tuple[Path, ...]:
    return tuple(
        Path("scrapers") / domain / "entrypoint.py"
        for domain in sorted(get_domain_entrypoint_scraper_metadata())
    )

ENTRYPOINT_MODULES = ARCHITECTURE_REGISTRY.entrypoint_files


@dataclass(frozen=True)
class ConfigBlockSemantics:
    path: str
    lineno: int
    callee: str
    domain_name: str
    url_source: str
    parser_source: str
    record_factory_source: str
    section_source: str
    semantic_key: tuple[str, str, str, str, str]


# Pozwalamy na bloki "prawie takie same" tylko tam, gdzie to czytelna, intencjonalna
# para i utrzymywanie dwóch jawnych konfiguracji jest tańsze niż nad-abstrakcja.
ALLOWED_SIMILAR_CONFIG_BLOCKS: dict[frozenset[str], str] = {
    frozenset(
        {
            "scrapers/grands_prix/red_flagged_races_scraper/world_championship.py",
            "scrapers/grands_prix/red_flagged_races_scraper/non_championship.py",
        },
    ): (
        "Dwie listy czerwonych flag mają wspólne źródło/kolumny, ale różnią się "
        "znaczeniem sekcji (world championship vs non-championship) i są utrzymywane "
        "jako osobne, jawne punkty wejścia domeny."
    ),
    frozenset(
        {
            "scrapers/points/points_scoring_systems_history.py",
            "scrapers/points/shortened_race_points.py",
            "scrapers/points/sprint_qualifying_points.py",
        },
    ): (
        "Punkty współdzielą URL i record_factory mapping(), ale różne parsery schematów "
        "odwzorowują inne tabele wiki; ich podobieństwo jest zamierzone i domenowo jawne."
    ),
}


def _ast_expr_to_str(node: ast.AST | None) -> str:
    if node is None:
        return "<missing>"
    if hasattr(ast, "unparse"):
        return ast.unparse(node)
    return ast.dump(node, include_attributes=False)


def _callee_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_callee_name(node.value)}.{node.attr}"
    return _ast_expr_to_str(node)


def _domain_name_from_path(path: Path) -> str:
    try:
        idx = path.parts.index("scrapers")
    except ValueError:
        return "unknown"
    if idx + 1 >= len(path.parts):
        return "unknown"
    return path.parts[idx + 1]


def _semantic_signature_from_assign(path: Path, node: ast.Assign) -> ConfigBlockSemantics:
    value = node.value
    domain_name = _domain_name_from_path(path)

    if not isinstance(value, ast.Call):
        raw = _ast_expr_to_str(value)
        return ConfigBlockSemantics(
            path=str(path),
            lineno=node.lineno,
            callee="<non-call-config>",
            domain_name=domain_name,
            url_source=raw,
            parser_source=raw,
            record_factory_source=raw,
            section_source=raw,
            semantic_key=("<non-call-config>", domain_name, raw, raw, raw),
        )

    kwargs = {kw.arg: kw.value for kw in value.keywords if kw.arg}

    url_source = _ast_expr_to_str(kwargs.get("url"))
    parser_node = kwargs.get("schema") or kwargs.get("columns")
    parser_source = _ast_expr_to_str(parser_node)
    record_factory_source = _ast_expr_to_str(kwargs.get("record_factory"))
    section_source = _ast_expr_to_str(kwargs.get("section_id"))
    callee = _callee_name(value.func)

    return ConfigBlockSemantics(
        path=str(path),
        lineno=node.lineno,
        callee=callee,
        domain_name=domain_name,
        url_source=url_source,
        parser_source=parser_source,
        record_factory_source=record_factory_source,
        section_source=section_source,
        semantic_key=(callee, domain_name, url_source, section_source, parser_source),
    )


def _collect_semantic_config_blocks() -> list[ConfigBlockSemantics]:
    blocks: list[ConfigBlockSemantics] = []

    for py_file in Path("scrapers").rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            if not any(
                isinstance(target, ast.Name) and target.id == "CONFIG"
                for target in node.targets
            ):
                continue
            blocks.append(_semantic_signature_from_assign(py_file, node))

    return blocks


def _iter_non_whitelisted_duplicate_groups(
    blocks: list[ConfigBlockSemantics],
) -> list[list[ConfigBlockSemantics]]:
    grouped: dict[tuple[str, str, str, str, str], list[ConfigBlockSemantics]] = defaultdict(list)
    for block in blocks:
        grouped[block.semantic_key].append(block)

    duplicates = [items for items in grouped.values() if len(items) > 1]
    duplicates.sort(key=lambda items: (items[0].domain_name, items[0].url_source))

    non_whitelisted: list[list[ConfigBlockSemantics]] = []
    for group in duplicates:
        paths = frozenset(item.path for item in group)
        if paths in ALLOWED_SIMILAR_CONFIG_BLOCKS:
            continue
        non_whitelisted.append(group)

    return non_whitelisted


def _suggest_extraction_target(group: list[ConfigBlockSemantics]) -> str:
    domains = sorted({item.domain_name for item in group})
    if len(domains) == 1:
        return (
            "Wydziel wspólny builder/factory CONFIG do "
            f"`scrapers/{domains[0]}/.../config_factory.py` i wywołuj go z modułów list."
        )

    return (
        "Wydziel wspólny builder/factory CONFIG do `scrapers/base/...` (cross-domain) "
        f"dla domen: {', '.join(domains)}."
    )


def _build_duplicate_report(groups: list[list[ConfigBlockSemantics]]) -> str:
    lines = [
        "Wykryto semantycznie podobne bloki CONFIG (potencjalny copy-paste).",
        "Raport: co i gdzie wydzielić:",
    ]

    for idx, group in enumerate(groups, start=1):
        first = group[0]
        locations = ", ".join(f"{item.path}:{item.lineno}" for item in group)
        lines.extend(
            [
                f"{idx}. sygnatura={first.semantic_key}",
                f"   miejsca: {locations}",
                f"   parser={first.parser_source}",
                f"   record_factory={first.record_factory_source}",
                f"   rekomendacja: {_suggest_extraction_target(group)}",
            ],
        )

    return "\n".join(lines)


def test_no_duplicate_config_blocks() -> None:
    blocks = _collect_semantic_config_blocks()
    offenders = _iter_non_whitelisted_duplicate_groups(blocks)

    assert not offenders, _build_duplicate_report(offenders)


def test_duplicate_config_blocks_whitelist_has_justification() -> None:
    for paths, reason in ALLOWED_SIMILAR_CONFIG_BLOCKS.items():
        assert len(paths) > 1, "Whitelist entry must contain at least two files."
        assert reason.strip(), f"Whitelist entry {sorted(paths)} requires justification."


def test_domain_entrypoints_use_shared_factory_builders() -> None:
    for py_file in _entrypoint_module_paths():
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(py_file))

        assert "install_domain_entrypoint" in source

        local_dups = [
            node.name
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name in {"run_list_scraper", "__getattr__"}
        ]
        assert not local_dups, (
            "Entrypoint should not duplicate local wrappers. "
            "Use shared domain facade installer from scrapers.base.domain_entrypoint instead: "
            f"{py_file}"
        )
