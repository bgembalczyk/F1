# ruff: noqa: PLR2004
"""Tests for section parser hierarchy and content/body section wiring."""

from scrapers.wiki.parsers.body_content import BodyContentParser
from scrapers.wiki.parsers.content_text import ContentTextParser
from scrapers.wiki.parsers.sections.helpers import _split_into_parts
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_section import SubSubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import SubSubSubSectionParser
from tests.fixtures.wiki_parser_utils import as_root_children
from tests.fixtures.wiki_parser_utils import make_soup


def test_split_into_parts_no_headings() -> None:
    tags = as_root_children(make_soup("<div><p>A</p><p>B</p></div>"))

    parts = _split_into_parts(tags, "mw-heading2")

    assert len(parts) == 1
    assert parts[0][0] == "(Top)"
    assert parts[0][1] is None
    assert len(parts[0][2]) == 2


def test_split_into_parts_with_headings() -> None:
    html = """
    <div>
      <p>Intro</p>
      <div class="mw-heading mw-heading2"><h2 id="Sec1">Sec1</h2></div>
      <p>Content 1</p>
      <div class="mw-heading mw-heading2"><h2 id="Sec2">Sec2</h2></div>
      <p>Content 2</p>
    </div>
    """

    parts = _split_into_parts(as_root_children(make_soup(html)), "mw-heading2")

    assert len(parts) == 3
    assert parts[0][0] == "(Top)"
    assert parts[1][0] == "Sec1"
    assert parts[1][1] == "Sec1"
    assert parts[2][0] == "Sec2"


def test_sub_sub_sub_section_parser() -> None:
    html = """
    <div>
      <p>Some text</p>
      <ul><li>Item A</li></ul>
    </div>
    """

    result = SubSubSubSectionParser().parse(make_soup(html).find("div"))

    assert "elements" in result
    assert len(result["elements"]) == 2
    types = {element["kind"] for element in result["elements"]}
    assert "paragraph" in types
    assert "list" in types


def test_sub_sub_section_parser_divides_into_sub_sub_sub_sections() -> None:
    html = """
    <div>
      <p>Intro</p>
      <div class="mw-heading mw-heading5"><h5 id="Sub5_One">Sub5 One</h5></div>
      <p>Content 5-1</p>
      <div class="mw-heading mw-heading5"><h5 id="Sub5_Two">Sub5 Two</h5></div>
      <p>Content 5-2</p>
    </div>
    """

    result = SubSubSectionParser().parse(make_soup(html).find("div"))

    sections = result["sub_sub_sub_sections"]
    assert len(sections) == 3
    assert sections[0]["section_label"] == "(Top)"
    assert sections[1]["section_label"] == "Sub5 One"
    assert sections[2]["section_label"] == "Sub5 Two"


def test_sub_section_parser_divides_into_sub_sub_sections() -> None:
    html = """
    <div>
      <div class="mw-heading mw-heading4"><h4 id="Level4">Level 4</h4></div>
      <p>Content</p>
    </div>
    """

    result = SubSectionParser().parse(make_soup(html).find("div"))

    sections = result["sub_sub_sections"]
    assert sections[0]["section_label"] == "(Top)"
    assert sections[1]["section_label"] == "Level 4"


def test_section_parser_divides_into_sub_sections() -> None:
    html = """
    <div>
      <p>Intro</p>
      <div class="mw-heading mw-heading3"><h3 id="Sub_A">Sub A</h3></div>
      <p>Sub A content</p>
    </div>
    """

    result = SectionParser().parse(make_soup(html).find("div"))

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

    assert SubSubSectionParser().parse(make_soup(html).find("div")) == {
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
    result = SubSectionParser().parse(make_soup(html).find("div"))

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
    result = SectionParser().parse(make_soup(html).find("div"))

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


def test_content_text_parser_divides_into_sections() -> None:
    html = """
    <div id="mw-content-text" class="mw-body-content">
      <p>Introduction</p>
      <div class="mw-heading mw-heading2"><h2 id="Early_life">Early life</h2></div>
      <p>Born in Stevenage</p>
      <div class="mw-heading mw-heading2"><h2 id="Career">Career</h2></div>
      <p>Career content</p>
    </div>
    """

    sections = ContentTextParser().parse(make_soup(html).find("div"))["sections"]

    assert len(sections) == 3
    assert sections[0]["section_label"] == "(Top)"
    assert sections[1]["section_label"] == "Early life"
    assert sections[2]["section_label"] == "Career"


def test_body_content_parser() -> None:
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

    result = BodyContentParser().parse(make_soup(html).find("div", id="bodyContent"))

    assert result["content_text"] is not None
    sections = result["content_text"]["sections"]
    assert sections[0]["section_label"] == "(Top)"
    assert sections[1]["section_label"] == "History"
    assert result["category_links"] is not None


def test_body_content_parser_find() -> None:
    html = """
    <html><body>
      <div id="bodyContent"><p>Content</p></div>
    </body></html>
    """

    body_content = BodyContentParser.find_body_content(make_soup(html))

    assert body_content is not None
    assert body_content.get("id") == "bodyContent"
