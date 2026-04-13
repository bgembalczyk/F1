from bs4 import BeautifulSoup

from scrapers.parsers.wiki.base_nested_section.sub_section.base import SubSectionParser
from scrapers.parsers.wiki.base_nested_section.sub_sub_section.base import (
    SubSubSectionParser,
)
from scrapers.parsers.wiki.content_text import ContentTextParser
from scrapers.parsers.wiki.sub_sub_sub_section import SubSubSubSectionParser


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def test_content_text_parser_no_heading_contract() -> None:
    html = '<div id="mw-content-text" class="mw-body-content"><p>Intro only</p></div>'

    result = ContentTextParser().parse(_soup(html).find("div"))

    assert len(result["sections"]) == 1
    assert result["sections"][0]["section_label"] == "(Top)"
    assert result["sections"][0]["section_id"] == "top"


def test_content_text_parser_nested_list_and_table_contract() -> None:
    html = """
    <div id="mw-content-text" class="mw-body-content">
      <div class="mw-heading mw-heading2"><h2 id="History">History</h2></div>
      <div class="mw-heading mw-heading3"><h3 id="Origins">Origins</h3></div>
      <ul><li>First era</li></ul>
      <table class="wikitable"><tr><th>Year</th></tr><tr><td>1950</td></tr></table>
    </div>
    """

    result = ContentTextParser().parse(_soup(html).find("div"))

    origins = result["sections"][1]["sub_sections"][1]
    leaf = origins["sub_sub_sections"][0]["sub_sub_sub_sections"][0]
    assert [item["kind"] for item in leaf["elements"]] == ["list", "table"]


def test_content_text_parser_alternative_section_id_anchor_contract() -> None:
    html = """
    <div id="mw-content-text" class="mw-body-content">
      <div class="mw-heading mw-heading2">
        <h2 id="Constructors_for_the_2026_season">Constructors for the 2026 season</h2>
      </div>
      <p>Lineup</p>
    </div>
    """

    result = ContentTextParser().parse(_soup(html).find("div"))

    assert result["sections"][1]["section_id"] == "constructors_for_the_2026_season"


def test_sublevel_parsers_are_compatible_adapters() -> None:
    assert SubSectionParser.heading_class == "mw-heading4"
    assert SubSubSectionParser.heading_class == "mw-heading5"
    assert callable(SubSubSubSectionParser().parse_group)
