#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import Any

SCRAPER_DOMAIN_PARTS = 3
PARSER_NAMING_SCOPE = (
    Path("scrapers/infobox/parsers/providers"),
    Path("scrapers/infobox/parsers/bundles"),
    Path("scrapers/parsers/mixins"),
    Path("scrapers/parsers/rules.py"),
)
PARSER_COMPAT_ALIAS = ("SectionParser", "SectionParserABC")
PARSER_PROTOCOL_IMPORT_PREFIX = "scrapers.parsers.section"
PARSER_CONTRACT_SCOPES = (
    Path("scrapers/parsers/section"),
    Path("scrapers/parsers/wiki/base_nested_section"),
)
PARSER_ABSTRACT_BASE_NAMES = {
    "SectionParserBase",
    "BaseNestedSectionParser",
    "TableSectionParser",
    "ConstructorTablesSectionParser",
    "ConstructorsSectionParser",
    "NestedWikiSectionParser",
    "SubSectionParser",
    "SubSubSectionParser",
    "WikiTableHtmlParser",
}


def load_architecture_rules() -> Any:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from tests.architecture import rules

    return rules


def iter_layer_files(
    domain_dir: Path,
    domain: str,
    rules: Any,
) -> list[tuple[Path, str]]:
    collected: list[tuple[Path, str]] = []
    for py_file in domain_dir.rglob("*.py"):
        layer = rules.infer_layer(py_file, domain=domain)
        if layer in rules.LAYERS:
            collected.append((py_file, layer))
    return collected


def detect_relevant_domains(
    changed_files: list[Path],
    *,
    domains: tuple[str, ...],
) -> set[str]:
    selected: set[str] = set()
    for file_path in changed_files:
        parts = file_path.parts
        if (
            len(parts) >= SCRAPER_DOMAIN_PARTS
            and parts[0] == "scrapers"
            and parts[1] in domains
        ):
            selected.add(parts[1])
    return selected


def check_required_layout(
    root: Path,
    domains: tuple[str, ...],
    rules: Any,
) -> list[str]:
    violations: list[str] = []
    for domain in domains:
        domain_dir = root / domain
        if not domain_dir.exists():
            violations.append(f"Missing domain directory: {domain_dir}")
            continue

        entrypoint = domain_dir / "entrypoint.py"
        if not entrypoint.exists():
            violations.append(f"Missing facade entrypoint in domain: {domain}")

        available_layers = {
            layer for _, layer in iter_layer_files(domain_dir, domain, rules)
        }
        missing_layers = set(rules.REQUIRED_LAYERS_BY_DOMAIN[domain]) - available_layers
        if missing_layers:
            violations.append(
                f"Missing layer modules for {domain}: {sorted(missing_layers)}",
            )
    return violations


def check_layer_boundaries(
    root: Path,
    domains: tuple[str, ...],
    rules: Any,
) -> list[str]:
    violations: list[str] = []
    for domain in domains:
        domain_dir = root / domain
        if not domain_dir.exists():
            continue

        for py_file, layer in iter_layer_files(domain_dir, domain, rules):
            targets = rules.resolve_import_targets(py_file)
            forbidden = rules.FORBIDDEN_IMPORTS_BY_LAYER[layer]
            for forbidden_target in forbidden:
                dotted = f"scrapers.{domain}.{forbidden_target}"
                if any(
                    target == dotted or target.startswith(f"{dotted}.")
                    for target in targets
                ):
                    violations.append(
                        "Layer boundary violation: "
                        f"{py_file} imports {dotted}; targets={targets}",
                    )
    return violations


def check_cross_domain_imports(
    root: Path,
    domains: tuple[str, ...],
    rules: Any,
) -> list[str]:
    violations: list[str] = []
    for domain in domains:
        domain_dir = root / domain
        if not domain_dir.exists():
            continue

        for py_file in domain_dir.rglob("*.py"):
            cross_domain = rules.collect_cross_domain_import_violations(py_file, domain)
            if cross_domain:
                uniq = sorted(set(cross_domain))
                violations.append(f"Cross-domain import in {py_file}: {uniq}")
    return violations


def check_sections_single_scraper_boundary(
    root: Path,
    domains: tuple[str, ...],
    rules: Any,
) -> list[str]:
    violations: list[str] = []
    for domain in domains:
        sections_dir = root / domain / "sections"
        if not sections_dir.exists():
            continue

        for py_file in sections_dir.glob("*.py"):
            imports = rules.collect_single_scraper_import_violations(py_file, domain)
            if imports:
                violations.append(
                    "Forbidden import direction sections/ -> single_scraper.py "
                    f"in {py_file}: {imports}",
                )
    return violations


def _is_in_parser_naming_scope(path: Path) -> bool:
    return any(path == scope or scope in path.parents for scope in PARSER_NAMING_SCOPE)


def check_parser_naming_contracts() -> list[str]:
    violations: list[str] = []
    parser_abc_bases = {
        "ABC",
        "ParserABC",
        "BaseWikiParser",
        "SectionParserABC",
        "HtmlTagParserABC",
    }
    for py_file in Path("scrapers").rglob("*.py"):
        rel_path = py_file
        if not _is_in_parser_naming_scope(rel_path):
            continue
        module = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in module.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if not node.name.endswith("Parser"):
                continue
            has_parse = any(
                isinstance(item, ast.FunctionDef) and item.name == "parse"
                for item in node.body
            )
            base_names = {base.id for base in node.bases if isinstance(base, ast.Name)}
            base_names |= {
                base.attr for base in node.bases if isinstance(base, ast.Attribute)
            }
            implements_parser_contract = bool(base_names & parser_abc_bases)
            if not has_parse and not implements_parser_contract:
                violations.append(
                    "Parser naming violation: "
                    f"{py_file}:{node.lineno} class {node.name} "
                    "uses '*Parser' suffix but does not define parse(...) "
                    "and does not inherit a parser ABC contract.",
                )
    return violations


def _matches_parser_protocol_module(module_name: str) -> bool:
    return module_name.startswith(PARSER_PROTOCOL_IMPORT_PREFIX) and (
        module_name == f"{PARSER_PROTOCOL_IMPORT_PREFIX}.protocol"
        or ".protocol." in module_name
        or module_name.endswith(".protocol")
    )


def check_parser_compat_imports_and_aliases() -> list[str]:
    violations: list[str] = []
    for py_file in Path("scrapers").rglob("*.py"):
        module = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(module):
            if isinstance(node, ast.ImportFrom) and node.module:
                if _matches_parser_protocol_module(node.module):
                    violations.append(
                        "Forbidden parser compat import: "
                        f"{py_file}:{node.lineno} imports from '{node.module}'. "
                        "Use canonical parser ABC modules directly.",
                    )
                for alias in node.names:
                    if (
                        alias.name == PARSER_COMPAT_ALIAS[1]
                        and alias.asname == PARSER_COMPAT_ALIAS[0]
                    ):
                        violations.append(
                            "Forbidden parser compat alias: "
                            f"{py_file}:{node.lineno} uses "
                            f"'{PARSER_COMPAT_ALIAS[1]} as {PARSER_COMPAT_ALIAS[0]}'.",
                        )
                    if alias.name == PARSER_COMPAT_ALIAS[0]:
                        violations.append(
                            "Forbidden parser compat import: "
                            f"{py_file}:{node.lineno} imports '{PARSER_COMPAT_ALIAS[0]}'. "
                            "Use SectionParserABC directly.",
                        )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if _matches_parser_protocol_module(alias.name):
                        violations.append(
                            "Forbidden parser compat import: "
                            f"{py_file}:{node.lineno} imports '{alias.name}'. "
                            "Use canonical parser ABC modules directly.",
                        )
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == PARSER_COMPAT_ALIAS[0]:
                        if (
                            isinstance(node.value, ast.Name)
                            and node.value.id == PARSER_COMPAT_ALIAS[1]
                        ):
                            violations.append(
                                "Forbidden parser compat alias: "
                                f"{py_file}:{node.lineno} defines "
                                f"'{PARSER_COMPAT_ALIAS[0]} = {PARSER_COMPAT_ALIAS[1]}'.",
                            )
    return violations


def _base_name(base: ast.expr) -> str:
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    if isinstance(base, ast.Subscript):
        return _base_name(base.value)
    return ast.unparse(base)


def _is_abc_class(node: ast.ClassDef) -> bool:
    return "ABC" in {_base_name(base) for base in node.bases}


def _inherits_parser_abc(node: ast.ClassDef) -> bool:
    base_names = {_base_name(base) for base in node.bases}
    return any(name.endswith("ParserABC") for name in base_names) or bool(
        base_names & PARSER_ABSTRACT_BASE_NAMES,
    )


def check_parser_contract_enforcement() -> list[str]:
    violations: list[str] = []
    for scope in PARSER_CONTRACT_SCOPES:
        for py_file in scope.rglob("*.py"):
            module = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            for node in module.body:
                if not isinstance(node, ast.ClassDef):
                    continue
                if not node.name.endswith("Parser"):
                    continue
                has_parse = any(
                    isinstance(item, ast.FunctionDef) and item.name == "parse"
                    for item in node.body
                )
                if not _inherits_parser_abc(node):
                    violations.append(
                        "Parser contract violation: "
                        f"{py_file}:{node.lineno} class {node.name} "
                        "must inherit from parser ABC hierarchy.",
                    )
                    continue
                if not has_parse and not _is_abc_class(node):
                    violations.append(
                        "Parser contract violation: "
                        f"{py_file}:{node.lineno} class {node.name} "
                        "must define parse(...) or be abstract (ABC).",
                    )
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fast architecture boundary checks for local lint/CI.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional changed files (pre-commit mode).",
    )
    args = parser.parse_args()

    rules = load_architecture_rules()

    root = Path("scrapers")
    changed_files = [Path(path) for path in args.paths if path.endswith(".py")]
    relevant_domains = detect_relevant_domains(
        changed_files,
        domains=rules.DOMAINS,
    )

    if relevant_domains:
        full_domains = tuple(
            domain for domain in rules.ENTRYPOINT_DOMAINS if domain in relevant_domains
        )
        all_domains = tuple(
            domain for domain in rules.DOMAINS if domain in relevant_domains
        )
    else:
        full_domains = rules.ENTRYPOINT_DOMAINS
        all_domains = rules.DOMAINS

    errors = [
        *check_required_layout(root, full_domains, rules),
        *check_layer_boundaries(root, full_domains, rules),
        *check_sections_single_scraper_boundary(root, full_domains, rules),
        *check_cross_domain_imports(root, all_domains, rules),
        *check_parser_naming_contracts(),
        *check_parser_compat_imports_and_aliases(),
        *check_parser_contract_enforcement(),
    ]

    if errors:
        print("Architecture rules check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Architecture rules check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
