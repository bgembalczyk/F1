# ruff: noqa: SLF001
from pathlib import Path

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.constructors.constructors_list import ConstructorsListScraper
from scrapers.constructors.sections.list_section import CurrentConstructorsSectionParser
from scrapers.constructors.sections.list_section import FormerConstructorsSectionParser
from scrapers.seasons.parsers.results import SeasonResultsParser
from scrapers.seasons.parsers.table import SeasonTableParser
from tests._section_parser_fixture_pattern import ALIAS_FIXTURES

ALIAS_DOMAINS = ("constructors", "circuits", "seasons")
EXPECTED_PARSE_CALLS = 2


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
    ConstructorsListScraper._PARSE_SCOPE_CACHE.clear()
    scraper = ConstructorsListScraper(
        options=ScraperOptions(
            fetcher=FixtureFetcher(ALIAS_FIXTURES["constructors"]),
            include_urls=True,
        ),
        export_scope="current",
    )

    data = scraper.get_data()

    assert data
    assert data[0]["constructor"]["text"] == "Ferrari"
    assert data[0]["constructor"]["url"].endswith("/wiki/Ferrari")


def test_former_constructors_section_parser_handles_defunct_alias() -> None:
    ConstructorsListScraper._PARSE_SCOPE_CACHE.clear()
    scraper = ConstructorsListScraper(
        options=ScraperOptions(
            fetcher=FixtureFetcher(_fixture_html("former_constructors_alias.html")),
            include_urls=True,
        ),
        export_scope="former",
    )

    data = scraper.get_data()

    assert data
    assert data[0]["constructor"]["text"] == "Lotus"

    def _season_url(year: int) -> str:
        suffix = "Formula_One_season" if year <= 1980 else "Formula_One_World_Championship"
        return f"https://en.wikipedia.org/wiki/{year}_{suffix}"

    assert data[0]["seasons"] == [
        {"year": year, "url": _season_url(year)}
        for year in range(1958, 1995)
    ]


def test_former_constructors_parser_keeps_link_without_acronym() -> None:
    html = """
    <html><body>
      <h2><span id="Former_constructors">Former constructors</span></h2>
      <table class="wikitable">
        <tr>
          <th>Constructor</th><th>Licensed in</th><th>Seasons</th>
          <th>Races entered</th><th>Races started</th><th>Drivers</th>
          <th>Total entries</th><th>Wins</th><th>Points</th><th>Poles</th>
          <th>FL</th><th>Podiums</th><th>WCC</th><th>WDC</th>
        </tr>
        <tr>
          <td>
            <a href="/wiki/Automobiles_Gonfaronnaises_Sportives">
              Automobiles Gonfaronnaises Sportives
            </a>
            <span>(AGS)</span>
          </td>
          <td><a href="/wiki/France">France</a></td>
          <td>
            <a href="/wiki/1986_Formula_One_World_Championship">1986</a>-
            <a href="/wiki/1991_Formula_One_World_Championship">1991</a>
          </td>
          <td>80</td><td>32</td><td>10</td><td>124</td><td>0</td><td>2</td>
          <td>0</td><td>0</td><td>0</td><td>0</td><td>0</td>
        </tr>
      </table>
    </body></html>
    """
    ConstructorsListScraper._PARSE_SCOPE_CACHE.clear()
    scraper = ConstructorsListScraper(
        options=ScraperOptions(
            fetcher=FixtureFetcher(html),
            include_urls=True,
        ),
        export_scope="former",
    )

    data = scraper.get_data()

    assert data
    assert data[0]["constructor"] == {
        "text": "Automobiles Gonfaronnaises Sportives",
        "url": "https://en.wikipedia.org/wiki/Automobiles_Gonfaronnaises_Sportives",
    }


def test_former_constructors_parser_extracts_alias_names_with_common_url() -> None:
    html = """
    <html><body>
      <h2><span id="Former_constructors">Former constructors</span></h2>
      <table class="wikitable">
        <tr>
          <th>Constructor</th><th>Licensed in</th><th>Seasons</th>
          <th>Races entered</th><th>Races started</th><th>Drivers</th>
          <th>Total entries</th><th>Wins</th><th>Points</th><th>Poles</th>
          <th>FL</th><th>Podiums</th><th>WCC</th><th>WDC</th>
        </tr>
        <tr>
          <td>
            <a href="/wiki/Equipe_Ligier">Ligier</a>/
            <a href="/wiki/Equipe_Ligier">Talbot Ligier</a>
          </td>
          <td><a href="/wiki/France">France</a></td>
          <td>
            <a href="/wiki/1976_Formula_One_World_Championship">1976</a>-
            <a href="/wiki/1996_Formula_One_World_Championship">1996</a>
          </td>
          <td>326</td><td>325</td><td>31</td><td>326</td><td>9</td><td>388</td>
          <td>20</td><td>12</td><td>50</td><td>0</td><td>0</td>
        </tr>
      </table>
    </body></html>
    """
    parser = FormerConstructorsSectionParser(
        config=ConstructorsListScraper._FORMER_CONFIG,
        section_label="Former constructors",
        include_urls=True,
        normalize_empty_values=False,
    )
    section = BeautifulSoup(html, "html.parser")

    data = parser.parse(section).records

    assert data
    assert data[0]["constructor"] == {
        "names": ["Ligier", "Talbot Ligier"],
        "url": "https://en.wikipedia.org/wiki/Equipe_Ligier",
    }


def test_circuits_section_parser_handles_formula_one_circuits_alias() -> None:
    scraper = CircuitsListScraper(
        options=ScraperOptions(
            fetcher=FixtureFetcher(ALIAS_FIXTURES["circuits"]),
            include_urls=True,
        ),
    )

    data = scraper.get_data()

    assert data
    assert data[0]["circuit"]["text"] == "Monza"
    assert data[0]["country"]["text"] == "Italy"


def test_seasons_results_parser_handles_results_and_standings_alias() -> None:
    soup = BeautifulSoup(ALIAS_FIXTURES["seasons"], "html.parser")
    parser = SeasonResultsParser(
        SeasonTableParser(
            options=ScraperOptions(),
            include_urls=True,
            url="https://en.wikipedia.org/wiki/2024_Formula_One_World_Championship",
        ),
    )

    rows = parser.parse(soup)

    assert rows
    assert rows[0]["round"] == 1
    assert rows[0]["grand_prix"]["text"] == "Bahrain Grand Prix"


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


def test_current_constructors_section_parser_retries_with_table_only_fragment() -> None:
    section_fragment = BeautifulSoup(
        """
        <div class="mw-heading mw-heading2">
          <h2 id="Constructors_for_the_2026_season">
            Constructors for the 2026 season
          </h2>
        </div>
        <table class="wikitable sortable">
          <tr>
            <th>Constructor</th><th>Engine</th><th>Licensed in</th><th>Based in</th>
            <th>Seasons</th><th>Races entered</th><th>Races started</th><th>Drivers</th>
            <th>Total entries</th><th>Wins</th><th>Points</th><th>Poles</th><th>FL</th>
            <th>Podiums</th><th>WCC</th><th>WDC</th><th>Antecedent teams</th>
          </tr>
          <tr>
            <td>Ferrari</td><td>Ferrari</td><td>Italy</td><td>Italy</td>
            <td>1950-present</td><td>1</td><td>1</td><td>2</td>
            <td>2</td><td>1</td><td>25</td><td>1</td><td>1</td>
            <td>2</td><td>16</td><td>15</td><td>—</td>
          </tr>
        </table>
        """,
        "html.parser",
    )

    parser = CurrentConstructorsSectionParser(
        config=ConstructorsListScraper._CURRENT_CONFIG,
        section_label="Current constructors",
        include_urls=False,
        normalize_empty_values=False,
    )

    call_count = 0
    original_parse = parser._parser.parse

    def flaky_parse(fragment: BeautifulSoup):
        nonlocal call_count
        call_count += 1
        has_heading = (
            fragment.find("h2", id="Constructors_for_the_2026_season") is not None
        )
        if has_heading:
            msg = "forced failure on full section fragment"
            raise RuntimeError(msg)
        return original_parse(fragment)

    parser._parser.parse = flaky_parse

    result = parser.parse(section_fragment)

    assert call_count == EXPECTED_PARSE_CALLS
    assert result.records
    assert result.records[0]["constructor"] == "Ferrari"
    assert list(result.records[0].keys()) == [
        "constructor",
        "engine",
        "antecedent_teams",
        "based_in",
        "drivers",
        "fastest_laps",
        "licensed_in",
        "podiums",
        "points",
        "poles",
        "races_entered",
        "races_started",
        "seasons",
        "total_entries",
        "wcc_titles",
        "wdc_titles",
        "wins",
    ]
