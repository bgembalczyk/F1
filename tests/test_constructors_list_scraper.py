from pathlib import Path

from bs4 import BeautifulSoup

from scrapers.base.single_wiki_article.section_selection_strategy import (
    WikipediaSectionByIdSelectionStrategy,
)
from scrapers.constructors.constructors_list import ConstructorsListScraper


def test_extract_current_section_uses_current_season_fallback_id() -> None:
    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "section_parsers"
        / "current_constructors_alias.html"
    )
    soup = BeautifulSoup(fixture_path.read_text(encoding="utf-8"), "html.parser")
    scraper = ConstructorsListScraper()
    selector = WikipediaSectionByIdSelectionStrategy(domain="constructors")

    section = scraper._extract_current_section(selector=selector, soup=soup)  # noqa: SLF001

    assert section is not None
    assert section.find("table", class_="wikitable") is not None
