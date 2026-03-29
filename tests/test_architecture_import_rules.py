from __future__ import annotations

from pathlib import Path

from tests.architecture.rules import DOMAINS
from tests.architecture.rules import resolve_import_targets

MIN_IMPORT_PARTS = 3


def _iter_cross_domain_imports(py_file: Path, domain: str) -> list[str]:
    violations: list[str] = []

    for target in resolve_import_targets(py_file):
        parts = target.split(".")
        if len(parts) < MIN_IMPORT_PARTS or parts[0] != "scrapers":
            continue

        imported_domain = parts[1]
        if imported_domain in DOMAINS and imported_domain != domain:
            violations.append(target)

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
