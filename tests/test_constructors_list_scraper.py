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


def test_extract_current_section_supports_hardcoded_2026_section_id() -> None:
    soup = BeautifulSoup(
        """
        <html><body>
          <div class="mw-heading mw-heading2">
            <h2 id="Constructors_for_the_2026_season">Constructors for the 2026 season</h2>
          </div>
          <p>Intro</p>
          <table class="wikitable sortable">
            <tr><th>Constructor</th><th>Engine</th><th>Licensed in</th><th>Based in</th></tr>
            <tr><td>Ferrari</td><td>Ferrari</td><td>Italy</td><td>Italy</td></tr>
          </table>
        </body></html>
        """,
        "html.parser",
    )
    scraper = ConstructorsListScraper()
    selector = WikipediaSectionByIdSelectionStrategy(domain="constructors")

    section = scraper._extract_current_section(selector=selector, soup=soup)  # noqa: SLF001

    assert section is not None
    assert section.find("h2", id="Constructors_for_the_2026_season") is not None
    assert section.find("table", class_="wikitable") is not None
