# ruff: noqa: SLF001
from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.sponsorship_liveries.parsers.splitters.record.facade import (
    SponsorshipRecordSplitter,
)
from scrapers.sponsorship_liveries.parsers.team_liveries import (
    TeamLiveriesSectionParser,
)
from scrapers.sponsorship_liveries.parsers.team_liveries import TeamLiveriesTableParser
from scrapers.sponsorship_liveries.scraper import F1SponsorshipLiveriesScraper


def test_sponsorship_scraper_uses_team_section_parser() -> None:
    scraper = F1SponsorshipLiveriesScraper(options=ScraperOptions())

    assert isinstance(scraper._section_parser, TeamLiveriesSectionParser)
    assert isinstance(scraper._section_parser._table_parser, TeamLiveriesTableParser)


def test_team_section_parser_splits_sections_and_uses_table_parser() -> None:
    parser = TeamLiveriesSectionParser(
        url="https://en.wikipedia.org/wiki/Formula_One_sponsorship_liveries",
        include_urls=True,
        normalize_empty_values=False,
        splitter=SponsorshipRecordSplitter(),
    )
    soup = BeautifulSoup(
        """
        <div id="bodyContent">
          <h2><span class="mw-headline" id="Team_A">Team A</span></h2>
          <table class="wikitable">
            <tr><th>Year</th><th>Main sponsor(s)</th></tr>
            <tr><td>2020</td><td>Alpha</td></tr>
          </table>
          <h2><span class="mw-headline" id="No_Table">No table</span></h2>
          <p>ignored</p>
        </div>
        """,
        "html.parser",
    )

    parsed = parser.parse_sections(soup)

    assert len(parsed) == 1
    assert parsed[0]["team"] == "Team A"
    assert parsed[0]["liveries"][0]["season"][0]["year"] == 2020
