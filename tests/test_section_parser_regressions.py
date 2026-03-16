from pathlib import Path

from scrapers.base.options import ScraperOptions
from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.constructors.current_constructors_list import CurrentConstructorsListScraper
from scrapers.constructors.former_constructors_list import FormerConstructorsListScraper


class FixtureFetcher:
    def __init__(self, html: str) -> None:
        self._html = html

    def get_text(self, _url: str, *, _timeout: int | None = None) -> str:
        return self._html

    def get(self, _url: str) -> str:
        return self._html


def _fixture_html(name: str) -> str:
    path = Path("tests/fixtures/section_parsers") / name
    return path.read_text(encoding="utf-8")


def test_current_constructors_section_parser_handles_current_season_alias() -> None:
    scraper = CurrentConstructorsListScraper(
        options=ScraperOptions(
            fetcher=FixtureFetcher(_fixture_html("current_constructors_alias.html")),
            include_urls=True,
        ),
    )

    data = scraper.get_data()

    assert data
    assert data[0]["constructor"]["text"] == "Ferrari"
    assert data[0]["constructor"]["url"].endswith("/wiki/Ferrari")


def test_former_constructors_section_parser_handles_defunct_alias() -> None:
    scraper = FormerConstructorsListScraper(
        options=ScraperOptions(
            fetcher=FixtureFetcher(_fixture_html("former_constructors_alias.html")),
            include_urls=True,
        ),
    )

    data = scraper.get_data()

    assert data
    assert data[0]["constructor"]["text"] == "Lotus"
    assert data[0]["seasons"] == [
        {
            "year": year,
            "url": f"https://en.wikipedia.org/wiki/{year}_Formula_One_World_Championship",
        }
        for year in range(1958, 1995)
    ]


def test_circuits_section_parser_handles_formula_one_circuits_alias() -> None:
    scraper = CircuitsListScraper(
        options=ScraperOptions(
            fetcher=FixtureFetcher(_fixture_html("circuits_alias.html")),
            include_urls=True,
        ),
    )

    data = scraper.get_data()

    assert data
    assert data[0]["circuit"]["text"] == "Monza"
    assert data[0]["country"]["text"] == "Italy"


def test_circuits_section_parser_falls_back_to_legacy_full_document_search() -> None:
    html = """
    <html><body>
      <h2><span id="Circuits">Circuits</span></h2>
      <p>Section exists but has no matching table.</p>

      <h2><span id="Other">Other</span></h2>
      <table class="wikitable">
        <tr><th>Circuit</th><th>Type</th><th>Location</th><th>Country</th></tr>
        <tr>
          <td><a href="/wiki/Spa-Francorchamps">Spa</a></td>
          <td>Permanent</td>
          <td>Stavelot</td>
          <td><a href="/wiki/Belgium">Belgium</a></td>
        </tr>
      </table>
    </body></html>
    """

    scraper = CircuitsListScraper(
        options=ScraperOptions(
            fetcher=FixtureFetcher(html),
            include_urls=True,
        ),
    )

    data = scraper.get_data()

    assert data
    assert data[0]["circuit"]["text"] == "Spa"
