from __future__ import annotations

from pathlib import Path

from scrapers.base.sections.critical_sections import DOMAIN_CRITICAL_SECTIONS

DOMAINS = ("drivers", "constructors", "circuits", "seasons", "grands_prix")


def test_sections_modules_do_not_import_single_scraper() -> None:
    root = Path("scrapers")
    for domain in DOMAINS:
        sections_dir = root / domain / "sections"
        for py_file in sections_dir.glob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            assert "single_scraper" not in source, f"Forbidden import in {py_file}"


def test_critical_sections_have_alias_fallbacks() -> None:
    for domain in DOMAINS:
        critical = DOMAIN_CRITICAL_SECTIONS.get(domain, ())
        assert critical, f"Missing critical sections map for domain={domain}"
        for section in critical:
            assert section.section_id.strip(), f"Empty section id in domain={domain}"
            assert section.alternative_section_ids, (
                f"Critical section without aliases in domain={domain}, "
                f"section={section.section_id}"
            )
