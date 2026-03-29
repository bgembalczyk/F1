# ruff: noqa: SLF001
"""Tests for parser-rule extension behaviour in wiki parser mixins."""

from scrapers.wiki.parsers.sections.data_classes import SectionExtractionContext
from scrapers.wiki.parsers.sections.sub_sub_sub_section import SubSubSubSectionParser
from tests.fixtures.wiki_parser_utils import make_soup


def test_wiki_element_parser_mixin_rules_priority_overlapping_table_classes() -> None:
    html = '<table class="infobox wikitable"><tr><td>Cell</td></tr></table>'
    parser = SubSubSubSectionParser()

    result = parser._parse_element(
        make_soup(html).find("table"),
        section_context=SectionExtractionContext(),
    )

    assert result is not None
    assert result["kind"] == "infobox"
    assert result["source_section_id"] is None


def test_wiki_element_parser_mixin_register_parser_rule_allows_domain_extensions(
) -> None:
    html = "<blockquote>Domain specific note</blockquote>"
    soup = make_soup(html)
    parser = SubSubSubSectionParser()

    parser.register_parser_rule(
        predicate=lambda el: el.name == "blockquote",
        parser=lambda el: {"text": el.get_text(" ", strip=True)},
        result_type="domain_blockquote",
        priority=0,
    )

    result = parser._parse_element(
        soup.find("blockquote"),
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
    soup = make_soup(html)
    parser = SubSubSubSectionParser()

    result = parser.parse_elements(
        list(soup.find("div").find_all(recursive=False)),
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
