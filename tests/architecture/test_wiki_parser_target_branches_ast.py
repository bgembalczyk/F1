from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

TARGET_BRANCHES = {
    "ParserABC",
    "HtmlTagParserABC",
    "HtmlSoupParserABC",
    "WikiTableElementParserABC",
    "WikiListElementParserABC",
    "WikiInfoboxElementParserABC",
    "WikiNavboxElementParserABC",
    "WikiFigureElementParserABC",
    "HtmlInfoboxFieldParser",
    "InfoboxRowsParser",
    # ABCs that serve as direct base contracts for concrete parsers
    "InfoboxFieldParserABC",  # legacy name kept for compatibility with historical checks
    "InfoboxHtmlFieldParserABC",
    "InfoboxRowsParserABC",
    "InfoboxNestedTableParserABC",
    "InfoboxCollapsibleTableParserABC",
    "TableParserABC",  # base of WikiTableBaseParser
}

ROOTS = (
    Path("scrapers/parsers/wiki"),
    Path("scrapers/parsers/infobox"),
    Path("scrapers/parsers/html_elements"),
    Path("scrapers/parsers/infobox/field"),
)


@dataclass(frozen=True)
class ClassInfo:
    name: str
    path: Path
    lineno: int
    bases: tuple[str, ...]
    has_parse: bool


def _base_name(base: ast.expr) -> str:
    text = ast.unparse(base)
    text = text.split("[", 1)[0]
    return text.split(".")[-1]


def _all_parser_classes() -> dict[str, ClassInfo]:
    classes: dict[str, ClassInfo] = {}
    for root in ROOTS:
        for path in sorted(root.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in tree.body:
                if not isinstance(node, ast.ClassDef) or not node.name.endswith(
                    "Parser",
                ):
                    continue
                bases = tuple(_base_name(base) for base in node.bases)
                has_parse = any(
                    isinstance(member, ast.FunctionDef) and member.name == "parse"
                    for member in node.body
                )
                classes[node.name] = ClassInfo(
                    name=node.name,
                    path=path,
                    lineno=node.lineno,
                    bases=bases,
                    has_parse=has_parse,
                )
    return classes


def _is_target_candidate(info: ClassInfo) -> bool:
    path_str = info.path.as_posix()
    if "scrapers/parsers/infobox/" in path_str:
        return True
    if "infobox/field" in path_str:
        return True
    if not info.name.startswith("Wiki"):
        return False
    return any(
        token in info.name
        for token in ("Table", "List", "Section", "Infobox", "Navbox", "Figure")
    )


def _descends_from_target(
    cls_name: str,
    classes: dict[str, ClassInfo],
    seen: set[str] | None = None,
) -> bool:
    if seen is None:
        seen = set()
    if cls_name in seen:
        return False
    seen.add(cls_name)

    info = classes.get(cls_name)
    if info is None:
        return cls_name in TARGET_BRANCHES

    for base in info.bases:
        if base in TARGET_BRANCHES:
            return True
        if base in classes and _descends_from_target(base, classes, seen):
            return True
    return False


def _has_parse_in_hierarchy(
    cls_name: str,
    classes: dict[str, ClassInfo],
    seen: set[str] | None = None,
) -> bool:
    if seen is None:
        seen = set()
    if cls_name in seen:
        return False
    seen.add(cls_name)

    info = classes.get(cls_name)
    if info is None:
        return cls_name in TARGET_BRANCHES

    if info.has_parse:
        return True

    return any(
        base in TARGET_BRANCHES
        or (base in classes and _has_parse_in_hierarchy(base, classes, seen))
        for base in info.bases
    )


def test_wiki_parser_classes_follow_target_branches_and_parse_contract() -> None:
    classes = _all_parser_classes()
    violations: list[str] = []

    for name, info in sorted(classes.items()):
        if not _is_target_candidate(info):
            continue
        if not _descends_from_target(name, classes):
            violations.append(
                f"{info.path}:{info.lineno} {name} does not inherit from target parser branches",
            )
            continue
        if not _has_parse_in_hierarchy(name, classes):
            violations.append(
                f"{info.path}:{info.lineno} {name} has no parse in hierarchy",
            )

    assert not violations, "\\n".join(violations)
