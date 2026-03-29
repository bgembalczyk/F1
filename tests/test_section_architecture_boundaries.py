from __future__ import annotations

from pathlib import Path

from scrapers.base.sections.constants import DOMAIN_SECTION_RESOLVER_CONFIG
from tests.architecture.rules import collect_single_scraper_import_violations

DOMAINS = ("drivers", "constructors", "circuits", "seasons", "grands_prix")


def test_sections_modules_do_not_import_single_scraper() -> None:
    root = Path("scrapers")
    for domain in DOMAINS:
        sections_dir = root / domain / "sections"
        for py_file in sections_dir.glob("*.py"):
            violations = collect_single_scraper_import_violations(py_file, domain)
            assert not violations, (
                "Forbidden import direction sections/ -> single_scraper.py "
                f"in {py_file}: {violations}"
            )


def test_single_scraper_can_depend_on_sections_without_reverse_dependency() -> None:
    root = Path("scrapers")
    for domain in DOMAINS:
        single_scraper_file = root / domain / "single_scraper.py"
        assert (
            single_scraper_file.exists()
        ), f"Missing single scraper file in domain: {single_scraper_file}"

        sections_dir = root / domain / "sections"
        violating_modules = [
            py_file
            for py_file in sections_dir.glob("*.py")
            if collect_single_scraper_import_violations(py_file, domain)
        ]
        assert not violating_modules, (
            "single_scraper.py may import sections/, but sections/ must not "
            f"import single_scraper.py for domain={domain}: {violating_modules}"
        )


def test_critical_sections_have_alias_fallbacks() -> None:
    for domain in DOMAINS:
        critical = DOMAIN_SECTION_RESOLVER_CONFIG.get(domain, ())
        assert critical, f"Missing critical sections map for domain={domain}"
        for section in critical:
            assert section.section_id.strip(), f"Empty section id in domain={domain}"
            assert section.alternative_section_ids, (
                f"Critical section without aliases in domain={domain}, "
                f"section={section.section_id}"
            )
