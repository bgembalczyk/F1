from __future__ import annotations

from pathlib import Path

from tests.architecture.rules import DOMAINS
from tests.architecture.rules import collect_cross_domain_import_violations


def test_domains_do_not_import_each_other_directly() -> None:
    root = Path("scrapers")
    for domain in DOMAINS:
        domain_dir = root / domain
        assert domain_dir.exists(), f"Missing domain package: {domain_dir}"

        violations_by_file: dict[str, list[str]] = {}
        for py_file in domain_dir.rglob("*.py"):
            violations = collect_cross_domain_import_violations(py_file, domain)
            if violations:
                violations_by_file[str(py_file)] = sorted(set(violations))

        assert not violations_by_file, (
            "Cross-domain imports are forbidden. Use scrapers.base abstractions "
            f"or other neutral layers instead. violations={violations_by_file}"
        )
