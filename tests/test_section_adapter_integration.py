# ruff: noqa: E501
from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.seasons.parsers.results import SeasonResultsParser
from scrapers.seasons.parsers.table import SeasonTableParser
from scrapers.wiki.parsers.content_text import ContentTextParser
from scrapers.wiki.parsers.section_adapter import collect_section_elements
from scrapers.wiki.parsers.section_adapter import find_section_tree


def test_find_section_tree_with_multilevel_sections_and_alias() -> None:
    html = """
    <div id="bodyContent">
      <div id="mw-content-text" class="mw-body-content">
        <p>Intro</p>
        <div class="mw-heading mw-heading2"><h2 id="History">History</h2></div>
        <div class="mw-heading mw-heading3"><h3 id="Origins">Origins</h3></div>
        <p>Origins text</p>
        <div class="mw-heading mw-heading2"><h2 id="Grands_Prix">Grands Prix</h2></div>
        <div class="mw-heading mw-heading3"><h3 id="Rounds">Rounds</h3></div>
        <table class="wikitable">
          <tr><th>Round</th><th>Fastest lap</th><th>Winning driver</th><th>Report</th></tr>
          <tr><td>1</td><td>John Doe</td><td>John Doe</td><td><a href="/r1">Report</a></td></tr>
        </table>
      </div>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    content_text = soup.find("div", id="mw-content-text")
    article = ContentTextParser().parse(content_text)

    section = find_section_tree(article, "Results", {"grands prix"}, domain="seasons")

    assert section is not None
    assert section["section_id"] == "grands_prix"
    tables = collect_section_elements(section, "table")
    assert len(tables) == 1


def test_season_results_parser_uses_section_adapter_vertical_slice() -> None:
    html = """
    <div id="bodyContent">
      <div id="mw-content-text" class="mw-body-content">
        <div class="mw-heading mw-heading2"><h2 id="Season_summary">Season summary</h2></div>
        <table class="wikitable">
          <tr><th>Round</th><th>Winner</th></tr>
          <tr><td>1</td><td>Ignored</td></tr>
        </table>

        <div class="mw-heading mw-heading2"><h2 id="Grands_Prix">Grands Prix</h2></div>
        <div class="mw-heading mw-heading3"><h3 id="Rounds">Rounds</h3></div>
        <table class="wikitable">
          <tr><th>Round</th><th>Grand Prix</th><th>Fastest lap</th><th>Winning driver</th><th>Report</th></tr>
          <tr>
            <td>1</td>
            <td><a href="/wiki/Bahrain_Grand_Prix">Bahrain Grand Prix</a></td>
            <td>Max Verstappen</td>
            <td>Max Verstappen</td>
            <td><a href="/wiki/2024_Bahrain_Grand_Prix">Report</a></td>
          </tr>
        </table>
      </div>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    parser = SeasonResultsParser(
        SeasonTableParser(
            options=ScraperOptions(),
            include_urls=True,
            url="https://en.wikipedia.org/wiki/2024_Formula_One_World_Championship",
        ),
    )

    rows = parser.parse(soup)

    assert len(rows) == 1
    assert rows[0]["round"] == 1
    assert rows[0]["grand_prix"]["text"] == "Bahrain Grand Prix"
    assert rows[0]["winning_driver"]["text"] == "Max Verstappen"
