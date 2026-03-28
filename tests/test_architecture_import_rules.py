from __future__ import annotations

import ast
from pathlib import Path

DOMAINS = (
    "drivers",
    "constructors",
    "circuits",
    "seasons",
    "grands_prix",
    "engines",
    "points",
    "sponsorship_liveries",
    "tyres",
)
MIN_IMPORT_PARTS = 3


def _iter_cross_domain_imports(py_file: Path, domain: str) -> list[str]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    violations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                if len(parts) < MIN_IMPORT_PARTS or parts[0] != "scrapers":
                    continue
                imported_domain = parts[1]
                if imported_domain in DOMAINS and imported_domain != domain:
                    violations.append(alias.name)

        if isinstance(node, ast.ImportFrom):
            if node.level != 0 or node.module is None:
                continue
            parts = node.module.split(".")
            if len(parts) < MIN_IMPORT_PARTS or parts[0] != "scrapers":
                continue
            imported_domain = parts[1]
            if imported_domain in DOMAINS and imported_domain != domain:
                violations.append(node.module)

    return violations


def test_domains_do_not_import_each_other_directly() -> None:
    root = Path("scrapers")
    for domain in DOMAINS:
        domain_dir = root / domain
        assert domain_dir.exists(), f"Missing domain package: {domain_dir}"

        violations_by_file: dict[str, list[str]] = {}
        for py_file in domain_dir.rglob("*.py"):
            violations = _iter_cross_domain_imports(py_file, domain)
            if violations:
                violations_by_file[str(py_file)] = sorted(set(violations))

        assert not violations_by_file, (
            "Cross-domain imports are forbidden. Use scrapers.base abstractions "
            f"or other neutral layers instead. violations={violations_by_file}"
        )
