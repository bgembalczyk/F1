# ruff: noqa: PLR2004
"""Tests for wiki body/category and element parsers."""

from scrapers.wiki.parsers.category_links import CategoryLinksParser
from scrapers.wiki.parsers.elements.figure import FigureParser
from scrapers.wiki.parsers.elements.infobox import InfoboxParser
from scrapers.wiki.parsers.elements.list import ListParser
from scrapers.wiki.parsers.elements.navbox import NavBoxParser
from scrapers.wiki.parsers.elements.paragraph import ParagraphParser
from scrapers.wiki.parsers.elements.references_wrap import ReferencesWrapParser
from scrapers.wiki.parsers.elements.table import TableParser
from tests.fixtures.wiki_parser_utils import make_soup


def test_category_links_parser() -> None:
    html = """
    <div id="catlinks">
      <div id="mw-normal-catlinks">
        <a href="/wiki/Special:Categories">Categories</a>:
        <ul>
          <li><a href="/wiki/Category:1985_births">1985 births</a></li>
          <li><a href="/wiki/Category:British_people">British people</a></li>
        </ul>
      </div>
    </div>
    """
    parser = CategoryLinksParser()

    result = parser.parse(make_soup(html).find("div", id="catlinks"))

    assert "categories" in result
    assert len(result["categories"]) >= 1


def test_infobox_parser() -> None:
    html = """
    <table class="infobox vcard">
      <caption>Test Article</caption>
      <tr><th>Born</th><td>1985</td></tr>
      <tr><th>Nationality</th><td>British</td></tr>
    </table>
    """

    result = InfoboxParser().parse(make_soup(html).find("table"))

    assert result["title"] == "Test Article"
    assert result["rows"]["Born"] == "1985"
    assert result["rows"]["Nationality"] == "British"


def test_paragraph_parser() -> None:
    result = ParagraphParser().parse(make_soup("<p>Hello World</p>").find("p"))

    assert result["text"] == "Hello World"


def test_figure_parser() -> None:
    html = """
    <figure>
      <img src="image.jpg"/>
      <figcaption>A caption</figcaption>
    </figure>
    """

    result = FigureParser().parse(make_soup(html).find("figure"))

    assert result["caption"] == "A caption"
    assert result["src"] == "image.jpg"


def test_list_parser() -> None:
    html = "<ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul>"

    result = ListParser().parse(make_soup(html).find("ul"))

    assert result["items"] == ["Item 1", "Item 2", "Item 3"]


def test_table_parser() -> None:
    html = """
    <table class="wikitable">
      <tr><th>Name</th><th>Year</th></tr>
      <tr><td>Hamilton</td><td>2020</td></tr>
    </table>
    """

    result = TableParser().parse(make_soup(html).find("table"))

    assert result["headers"] == ["Name", "Year"]
    assert result["rows"] == [["Hamilton", "2020"]]


def test_table_parser_handles_multirow_headers_and_blank_th() -> None:
    html = """
    <table class="wikitable">
      <tr>
        <th rowspan="2">Pos</th>
        <th colspan="2">Driver</th>
        <th rowspan="2"></th>
        <th rowspan="2">Points</th>
      </tr>
      <tr>
        <th>Name</th>
        <th>Nationality</th>
      </tr>
      <tr>
        <td>1</td>
        <td>Lewis Hamilton</td>
        <td>British</td>
        <td>x</td>
        <td>413</td>
      </tr>
    </table>
    """

    result = TableParser().parse(make_soup(html).find("table"))

    assert result["headers"] == ["Pos", "Name", "Nationality", "Points"]
    assert result["rows"] == [["1", "Lewis Hamilton", "British", "413"]]
    assert result["raw_rows"] == [
        {
            "Pos": "1",
            "Name": "Lewis Hamilton",
            "Nationality": "British",
            "Points": "413",
        },
    ]


def test_table_parser_handles_rowspan_and_colspan_with_stable_mapping() -> None:
    html = """
    <table class="wikitable">
      <tr>
        <th>Year</th>
        <th>Grand Prix</th>
        <th>Result</th>
        <th>Notes</th>
      </tr>
      <tr>
        <td rowspan="2">1953</td>
        <td>Argentina</td>
        <td colspan="2">Win</td>
      </tr>
      <tr>
        <td>Monaco</td>
        <td>DNF</td>
        <td>Engine</td>
      </tr>
    </table>
    """

    result = TableParser().parse(make_soup(html).find("table"))

    assert result["headers"] == ["Year", "Grand Prix", "Result", "Notes"]
    assert result["rows"] == [
        ["1953", "Argentina", "Win", "Win"],
        ["1953", "Monaco", "DNF", "Engine"],
    ]
    assert result["raw_rows"][1]["Year"] == "1953"
    assert result["raw_rows"][1]["Grand Prix"] == "Monaco"


def test_navbox_parser() -> None:
    html = """
    <div role="navigation" class="navbox">
      <div class="navbox-title">Navigation</div>
      <a href="/wiki/Topic1">Topic 1</a>
      <a href="/wiki/Topic2">Topic 2</a>
    </div>
    """

    result = NavBoxParser().parse(make_soup(html).find("div"))

    assert result["title"] == "Navigation"
    assert len(result["links"]) == 2


def test_references_wrap_parser() -> None:
    html = """
    <div class="references-wrap">
      <ol>
        <li>Reference 1</li>
        <li>Reference 2</li>
      </ol>
    </div>
    """

    result = ReferencesWrapParser().parse(make_soup(html).find("div"))

    assert len(result["references"]) == 2
