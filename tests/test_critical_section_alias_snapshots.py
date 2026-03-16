from pathlib import Path

from bs4 import BeautifulSoup

from scrapers.base.sections.critical_sections import DOMAIN_CRITICAL_SECTIONS
from scrapers.wiki.parsers.section_detection import find_section_heading


def _fixture(name: str) -> BeautifulSoup:
    html = (Path("tests/fixtures/section_parsers") / name).read_text(encoding="utf-8")
    return BeautifulSoup(html, "html.parser")


def test_critical_section_alias_snapshots_cover_all_target_domains() -> None:
    fixtures = {
        "drivers": "drivers_aliases.html",
        "constructors": "constructors_aliases.html",
        "circuits": "circuits_aliases.html",
        "seasons": "seasons_aliases.html",
        "grands_prix": "grands_prix_aliases.html",
    }

    for domain, fixture_name in fixtures.items():
        soup = _fixture(fixture_name)
        sections = DOMAIN_CRITICAL_SECTIONS[domain]

        matched = 0
        for critical in sections:
            match = find_section_heading(
                soup,
                critical.section_id,
                aliases={critical.section_id.lower().replace("_", " "): set(critical.alternative_section_ids)},
                domain=domain,
            )
            if match is not None:
                matched += 1

        assert matched >= 1, f"No critical alias resolved for domain={domain} fixture={fixture_name}"
