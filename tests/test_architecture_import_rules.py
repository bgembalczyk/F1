from __future__ import annotations

from pathlib import Path

from tests.architecture.registry import ARCHITECTURE_REGISTRY
from tests.support.imports_analyzer import parse_imports

DOMAINS = ARCHITECTURE_REGISTRY.domain_names
from tests.architecture.rules import DOMAINS
from tests.support.imports_analyzer import parse_imports

MIN_IMPORT_PARTS = 3


def _iter_cross_domain_imports(py_file: Path, domain: str) -> list[str]:
    violations: list[str] = []

    for parsed_import in parse_imports(py_file):
        if parsed_import.level != 0:
            continue
        parts = parsed_import.module.split(".")
        if len(parts) < MIN_IMPORT_PARTS or parts[0] != "scrapers":
            continue
        imported_domain = parts[1]
        if imported_domain in DOMAINS and imported_domain != domain:
            violations.append(parsed_import.module)

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
