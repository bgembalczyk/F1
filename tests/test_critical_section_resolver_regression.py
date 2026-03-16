from pathlib import Path

from bs4 import BeautifulSoup

from scrapers.base.sections.critical_sections import DOMAIN_CRITICAL_SECTIONS
from scrapers.base.sections.critical_sections import resolve_section_candidates
from scrapers.wiki.parsers.section_detection import find_section_heading


def _fixture(name: str) -> BeautifulSoup:
    html = (Path("tests/fixtures/section_parsers") / name).read_text(encoding="utf-8")
    return BeautifulSoup(html, "html.parser")


def test_each_critical_section_has_non_empty_fallback_and_resolves_alias_fixture() -> None:
    fixtures = {
        "drivers": "drivers_critical_aliases.html",
        "constructors": "constructors_critical_aliases.html",
        "circuits": "circuits_critical_aliases.html",
        "seasons": "seasons_critical_aliases.html",
        "grands_prix": "grands_prix_critical_aliases.html",
    }

    for domain, fixture_name in fixtures.items():
        soup = _fixture(fixture_name)
        for critical in DOMAIN_CRITICAL_SECTIONS[domain]:
            assert critical.alternative_section_ids, (
                f"Critical section without aliases: domain={domain} section={critical.section_id}"
            )

            candidates = resolve_section_candidates(
                domain=domain,
                section_id=critical.section_id,
                alternative_section_ids=critical.alternative_section_ids,
            )
            assert candidates[0] == critical.section_id
            assert len(candidates) >= 3

            match = None
            for candidate in candidates:
                match = find_section_heading(soup, candidate, domain=domain)
                if match is not None:
                    break

            assert match is not None, (
                f"No resolver candidate matched for domain={domain} section={critical.section_id}"
            )
