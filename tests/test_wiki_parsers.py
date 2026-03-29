# ruff: noqa: PLC0415, PLR2004, SLF001
"""Tests for wiki parsers hierarchy."""

import pytest
from bs4 import BeautifulSoup

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.body_content import BodyContentParser
from scrapers.wiki.parsers.category_links import CategoryLinksParser
from scrapers.wiki.parsers.content_text import ContentTextParser
from scrapers.wiki.parsers.elements.figure import FigureParser
from scrapers.wiki.parsers.elements.infobox import InfoboxParser
from scrapers.wiki.parsers.elements.list import ListParser
from scrapers.wiki.parsers.elements.navbox import NavBoxParser
from scrapers.wiki.parsers.elements.paragraph import ParagraphParser
from scrapers.wiki.parsers.elements.references_wrap import ReferencesWrapParser
from scrapers.wiki.parsers.elements.table import TableParser
from scrapers.wiki.parsers.header import HeaderParser
from scrapers.wiki.parsers.sections.data_classes import SectionExtractionContext
from scrapers.wiki.parsers.sections.helpers import _split_into_parts
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_section import SubSubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import SubSubSubSectionParser

# ---------------------------------------------------------------------------
# WikiParser is abstract
# ---------------------------------------------------------------------------


def test_wiki_parser_is_abstract():
    with pytest.raises(TypeError):
        WikiParser()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# _split_into_parts helper
# ---------------------------------------------------------------------------


def _make_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def test_split_into_parts_no_headings():
    html = "<div><p>A</p><p>B</p></div>"
    soup = _make_soup(html)
    from bs4 import Tag

    tags = [c for c in soup.find("div").children if isinstance(c, Tag)]
    parts = _split_into_parts(tags, "mw-heading2")
    assert len(parts) == 1
    assert parts[0][0] == "(Top)"
    assert parts[0][1] is None
    assert len(parts[0][2]) == 2


def test_split_into_parts_with_headings():
    html = """
    <div>
      <p>Intro</p>
      <div class="mw-heading mw-heading2"><h2 id="Sec1">Sec1</h2></div>
      <p>Content 1</p>
      <div class="mw-heading mw-heading2"><h2 id="Sec2">Sec2</h2></div>
      <p>Content 2</p>
    </div>
    """
    soup = _make_soup(html)
    from bs4 import Tag

    tags = [c for c in soup.find("div").children if isinstance(c, Tag)]
    parts = _split_into_parts(tags, "mw-heading2")
    assert len(parts) == 3
    assert parts[0][0] == "(Top)"
    assert parts[1][0] == "Sec1"
    assert parts[1][1] == "Sec1"
    assert parts[2][0] == "Sec2"


# ---------------------------------------------------------------------------
# HeaderParser
# ---------------------------------------------------------------------------


def test_header_parser_extracts_title():
    html = """
    <header class="mw-body-header vector-page-titlebar no-font-mode-scale">
      <h1 class="mw-page-title-main">Lewis Hamilton</h1>
    </header>
    """
    soup = _make_soup(html)
    parser = HeaderParser()
    header_el = soup.find("header")
    result = parser.parse(header_el)
    assert result["title"] == "Lewis Hamilton"


def test_header_parser_find_header():
    html = """
    <html><body>
      <header class="mw-body-header vector-page-titlebar">
        <h1>Title</h1>
      </header>
    </body></html>
    """
    soup = _make_soup(html)
    header_el = HeaderParser.find_header(soup)
    assert header_el is not None
    assert header_el.name == "header"


def test_header_parser_find_header_returns_none_when_absent():
    soup = _make_soup("<html><body><div>No header here</div></body></html>")
    assert HeaderParser.find_header(soup) is None


# ---------------------------------------------------------------------------
# CategoryLinksParser
# ---------------------------------------------------------------------------


def test_category_links_parser():
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
    soup = _make_soup(html)
    parser = CategoryLinksParser()
    result = parser.parse(soup.find("div", id="catlinks"))
    assert "categories" in result
    assert len(result["categories"]) >= 1


# ---------------------------------------------------------------------------
# Element parsers
# ---------------------------------------------------------------------------


def test_infobox_parser():
    html = """
    <table class="infobox vcard">
      <caption>Test Article</caption>
      <tr><th>Born</th><td>1985</td></tr>
      <tr><th>Nationality</th><td>British</td></tr>
    </table>
    """
    soup = _make_soup(html)
    parser = InfoboxParser()
    result = parser.parse(soup.find("table"))
    assert result["title"] == "Test Article"
    assert result["rows"]["Born"] == "1985"
    assert result["rows"]["Nationality"] == "British"


def test_paragraph_parser():
    html = "<p>Hello World</p>"
    soup = _make_soup(html)
    parser = ParagraphParser()
    result = parser.parse(soup.find("p"))
    assert result["text"] == "Hello World"


def test_figure_parser():
    html = """
    <figure>
      <img src="image.jpg"/>
      <figcaption>A caption</figcaption>
    </figure>
    """
    soup = _make_soup(html)
    parser = FigureParser()
    result = parser.parse(soup.find("figure"))
    assert result["caption"] == "A caption"
    assert result["src"] == "image.jpg"


def test_list_parser():
    html = "<ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul>"
    soup = _make_soup(html)
    parser = ListParser()
    result = parser.parse(soup.find("ul"))
    assert result["items"] == ["Item 1", "Item 2", "Item 3"]


def test_table_parser():
    html = """
    <table class="wikitable">
      <tr><th>Name</th><th>Year</th></tr>
      <tr><td>Hamilton</td><td>2020</td></tr>
    </table>
    """
    soup = _make_soup(html)
    parser = TableParser()
    result = parser.parse(soup.find("table"))
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
    soup = _make_soup(html)
    parser = TableParser()

    result = parser.parse(soup.find("table"))

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
    soup = _make_soup(html)
    parser = TableParser()

    result = parser.parse(soup.find("table"))

    assert result["headers"] == ["Year", "Grand Prix", "Result", "Notes"]
    assert result["rows"] == [
        ["1953", "Argentina", "Win", "Win"],
        ["1953", "Monaco", "DNF", "Engine"],
    ]
    assert result["raw_rows"][1]["Year"] == "1953"
    assert result["raw_rows"][1]["Grand Prix"] == "Monaco"


def test_navbox_parser():
    html = """
    <div role="navigation" class="navbox">
      <div class="navbox-title">Navigation</div>
      <a href="/wiki/Topic1">Topic 1</a>
      <a href="/wiki/Topic2">Topic 2</a>
    </div>
    """
    soup = _make_soup(html)
    parser = NavBoxParser()
    result = parser.parse(soup.find("div"))
    assert result["title"] == "Navigation"
    assert len(result["links"]) == 2


def test_references_wrap_parser():
    html = """
    <div class="references-wrap">
      <ol>
        <li>Reference 1</li>
        <li>Reference 2</li>
      </ol>
    </div>
    """
    soup = _make_soup(html)
    parser = ReferencesWrapParser()
    result = parser.parse(soup.find("div"))
    assert len(result["references"]) == 2


# ---------------------------------------------------------------------------
# Section parsers hierarchy
# ---------------------------------------------------------------------------


def test_sub_sub_sub_section_parser():
    html = """
    <div>
      <p>Some text</p>
      <ul><li>Item A</li></ul>
    </div>
    """
    soup = _make_soup(html)
    parser = SubSubSubSectionParser()
    result = parser.parse(soup.find("div"))
    assert "elements" in result
    assert len(result["elements"]) == 2
    types = {e["kind"] for e in result["elements"]}
    assert "paragraph" in types
    assert "list" in types


def test_section_parsers_support_cooperative_init_mro() -> None:
    calls: list[str] = []

    class InitTrackerMixin:
        def __init__(self, *args: object, **kwargs: object) -> None:
            calls.append("tracker")
            super().__init__(*args, **kwargs)

    class ProbeSubSubSubParser(InitTrackerMixin, SubSubSubSectionParser):
        def __init__(self) -> None:
            calls.append("sub_sub_sub")
            super().__init__()

    class ProbeSectionParser(InitTrackerMixin, SectionParser):
        def __init__(self) -> None:
            calls.append("section")
            super().__init__()

    leaf_parser = ProbeSubSubSubParser()
    top_parser = ProbeSectionParser()

    assert calls == ["sub_sub_sub", "tracker", "section", "tracker"]
    assert hasattr(leaf_parser, "_parser_rules")
    assert isinstance(top_parser.child_parser, SubSectionParser)
    assert isinstance(top_parser.child_parser.child_parser, SubSubSectionParser)
    assert isinstance(
        top_parser.child_parser.child_parser.child_parser,
        SubSubSubSectionParser,
    )


def test_wiki_element_parser_mixin_rules_priority_overlapping_table_classes() -> None:
    html = '<table class="infobox wikitable"><tr><td>Cell</td></tr></table>'
    soup = _make_soup(html)
    parser = SubSubSubSectionParser()

    result = parser._parse_element(
        soup.find("table"),
        section_context=SectionExtractionContext(),
    )

    assert result is not None
    assert result["kind"] == "infobox"
    assert result["source_section_id"] is None


def test_wiki_element_parser_mixin_register_parser_rule_allows_domain_extensions():
    html = "<blockquote>Domain specific note</blockquote>"
    soup = _make_soup(html)
    parser = SubSubSubSectionParser()
    blockquote = soup.find("blockquote")

    parser.register_parser_rule(
        predicate=lambda el: el.name == "blockquote",
        parser=lambda el: {"text": el.get_text(" ", strip=True)},
        result_type="domain_blockquote",
        priority=0,
    )

    result = parser._parse_element(
        blockquote,
        section_context=SectionExtractionContext(),
    )

    assert result["kind"] == "domain_blockquote"
    assert result["data"] == {"text": "Domain specific note"}
    assert "raw_html_fragment" in result


def test_wiki_element_parser_mixin_default_registry_matches_expected_types() -> None:
    html = """
    <div>
      <p>Ala ma kota.</p>
      <figure><img src="/img.png" alt="x" /></figure>
      <ul><li>one</li></ul>
      <table class="infobox"><tr><th>A</th><td>B</td></tr></table>
      <table class="wikitable"><tr><th>A</th></tr><tr><td>B</td></tr></table>
      <div role="navigation" class="navbox"><div class="navbox-title">N</div></div>
      <div class="foo references-wrap bar"><ol><li>Ref</li></ol></div>
    </div>
    """
    soup = _make_soup(html)
    parser = SubSubSubSectionParser()
    root = soup.find("div")

    result = parser.parse_elements(
        list(root.find_all(recursive=False)),
        section_context=SectionExtractionContext(section_id="demo"),
    )

    assert [item["kind"] for item in result] == [
        "paragraph",
        "figure",
        "list",
        "infobox",
        "table",
        "navbox",
        "references_wrap",
    ]


def test_sub_sub_section_parser_divides_into_sub_sub_sub_sections():
    html = """
    <div>
      <p>Intro</p>
      <div class="mw-heading mw-heading5"><h5 id="Sub5_One">Sub5 One</h5></div>
      <p>Content 5-1</p>
      <div class="mw-heading mw-heading5"><h5 id="Sub5_Two">Sub5 Two</h5></div>
      <p>Content 5-2</p>
    </div>
    """
    soup = _make_soup(html)
    parser = SubSubSectionParser()
    result = parser.parse(soup.find("div"))
    assert "sub_sub_sub_sections" in result
    sections = result["sub_sub_sub_sections"]
    assert len(sections) == 3
    assert sections[0]["section_label"] == "(Top)"
    assert sections[1]["section_label"] == "Sub5 One"
    assert sections[2]["section_label"] == "Sub5 Two"


def test_sub_section_parser_divides_into_sub_sub_sections():
    html = """
    <div>
      <div class="mw-heading mw-heading4"><h4 id="Level4">Level 4</h4></div>
      <p>Content</p>
    </div>
    """
    soup = _make_soup(html)
    parser = SubSectionParser()
    result = parser.parse(soup.find("div"))
    assert "sub_sub_sections" in result
    sections = result["sub_sub_sections"]
    assert sections[0]["section_label"] == "(Top)"
    assert sections[1]["section_label"] == "Level 4"


def test_section_parser_divides_into_sub_sections():
    html = """
    <div>
      <p>Intro</p>
      <div class="mw-heading mw-heading3"><h3 id="Sub_A">Sub A</h3></div>
      <p>Sub A content</p>
    </div>
    """
    soup = _make_soup(html)
    parser = SectionParser()
    result = parser.parse(soup.find("div"))
    assert "sub_sections" in result
    sub_sections = result["sub_sections"]
    assert len(sub_sections) == 2
    assert sub_sections[0]["section_label"] == "(Top)"
    assert sub_sections[1]["section_label"] == "Sub A"


def test_sub_sub_section_parser_snapshot_structure_regression() -> None:
    html = """
    <div>
      <p>Intro</p>
      <div class="mw-heading mw-heading5"><h5 id="Sub5_One">Sub5 One</h5></div>
      <p>Content 5-1</p>
    </div>
    """
    soup = _make_soup(html)
    parser = SubSubSectionParser()

    assert parser.parse(soup.find("div")) == {
        "sub_sub_sub_sections": [
            {
                "section_label": "(Top)",
                "section_id": "top",
                "elements": [
                    {
                        "kind": "paragraph",
                        "source_section_id": "top",
                        "confidence": 1.0,
                        "raw_html_fragment": "<p>Intro</p>",
                        "data": {"text": "Intro"},
                        "type": "paragraph",
                    },
                ],
            },
            {
                "section_label": "Sub5 One",
                "section_id": "sub5_one",
                "elements": [
                    {
                        "kind": "paragraph",
                        "source_section_id": "sub5_one",
                        "confidence": 1.0,
                        "raw_html_fragment": "<p>Content 5-1</p>",
                        "data": {"text": "Content 5-1"},
                        "type": "paragraph",
                    },
                ],
            },
        ],
    }


def test_sub_section_parser_snapshot_structure_regression() -> None:
    html = """
    <div>
      <p>Intro</p>
      <div class="mw-heading mw-heading4"><h4 id="Sub4_One">Sub4 One</h4></div>
      <p>Content 4-1</p>
      <div class="mw-heading mw-heading5"><h5 id="Sub5_One">Sub5 One</h5></div>
      <p>Content 5-1</p>
    </div>
    """
    soup = _make_soup(html)
    parser = SubSectionParser()
    result = parser.parse(soup.find("div"))

    assert result["sub_sub_sections"][0]["section_id"] == "top"
    assert (
        result["sub_sub_sections"][0]["sub_sub_sub_sections"][0]["section_id"]
        == "top__top"
    )
    assert result["sub_sub_sections"][1]["section_id"] == "sub4_one"
    assert (
        result["sub_sub_sections"][1]["sub_sub_sub_sections"][1]["section_id"]
        == "sub5_one"
    )


def test_section_parser_snapshot_structure_regression() -> None:
    html = """
    <div>
      <p>Intro</p>
      <div class="mw-heading mw-heading3"><h3 id="Sub3_One">Sub3 One</h3></div>
      <p>Content 3-1</p>
      <div class="mw-heading mw-heading4"><h4 id="Sub4_One">Sub4 One</h4></div>
      <p>Content 4-1</p>
      <div class="mw-heading mw-heading5"><h5 id="Sub5_One">Sub5 One</h5></div>
      <p>Content 5-1</p>
    </div>
    """
    soup = _make_soup(html)
    parser = SectionParser()
    result = parser.parse(soup.find("div"))

    assert result["sub_sections"][0]["section_id"] == "top"
    assert result["sub_sections"][1]["section_id"] == "sub3_one"
    assert (
        result["sub_sections"][1]["sub_sub_sections"][0]["section_id"]
        == "sub3_one__top"
    )
    assert result["sub_sections"][1]["sub_sub_sections"][1]["section_id"] == "sub4_one"
    assert (
        result["sub_sections"][1]["sub_sub_sections"][1]["sub_sub_sub_sections"][1][
            "section_id"
        ]
        == "sub5_one"
    )


# ---------------------------------------------------------------------------
# ContentTextParser
# ---------------------------------------------------------------------------


def test_content_text_parser_divides_into_sections():
    html = """
    <div id="mw-content-text" class="mw-body-content">
      <p>Introduction</p>
      <div class="mw-heading mw-heading2"><h2 id="Early_life">Early life</h2></div>
      <p>Born in Stevenage</p>
      <div class="mw-heading mw-heading2"><h2 id="Career">Career</h2></div>
      <p>Career content</p>
    </div>
    """
    soup = _make_soup(html)
    parser = ContentTextParser()
    result = parser.parse(soup.find("div"))
    sections = result["sections"]
    assert len(sections) == 3
    assert sections[0]["section_label"] == "(Top)"
    assert sections[1]["section_label"] == "Early life"
    assert sections[2]["section_label"] == "Career"


# ---------------------------------------------------------------------------
# BodyContentParser
# ---------------------------------------------------------------------------


def test_body_content_parser():
    html = """
    <div id="bodyContent">
      <div id="mw-content-text" class="mw-body-content mw-content-ltr">
        <p>Article intro</p>
        <div class="mw-heading mw-heading2"><h2 id="History">History</h2></div>
        <p>Historical content</p>
      </div>
      <div id="catlinks">
        <div id="mw-normal-catlinks">
          <a href="/wiki/Special:Categories">Categories</a>:
          <ul><li><a href="/wiki/Category:Test">Test category</a></li></ul>
        </div>
      </div>
    </div>
    """
    soup = _make_soup(html)
    parser = BodyContentParser()
    result = parser.parse(soup.find("div", id="bodyContent"))
    assert result["content_text"] is not None
    sections = result["content_text"]["sections"]
    assert sections[0]["section_label"] == "(Top)"
    assert sections[1]["section_label"] == "History"
    assert result["category_links"] is not None


def test_body_content_parser_find():
    html = """
    <html><body>
      <div id="bodyContent"><p>Content</p></div>
    </body></html>
    """
    soup = _make_soup(html)
    el = BodyContentParser.find_body_content(soup)
    assert el is not None
    assert el.get("id") == "bodyContent"
