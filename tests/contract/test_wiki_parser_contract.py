from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.wiki.parsers.body_content import BodyContentParser
from scrapers.wiki.parsers.category_links import CategoryLinksParser
from scrapers.wiki.parsers.content_text import ContentTextParser
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser
from scrapers.wiki.parsers.elements.figure import FigureParser
from scrapers.wiki.parsers.elements.infobox import InfoboxParser
from scrapers.wiki.parsers.elements.list_parser import ListParser
from scrapers.wiki.parsers.elements.navbox import NavBoxParser
from scrapers.wiki.parsers.elements.paragraph import ParagraphParser
from scrapers.wiki.parsers.elements.references_wrap import ReferencesWrapParser
from scrapers.wiki.parsers.elements.table import TableParser
from scrapers.wiki.parsers.header import HeaderParser
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_section import SubSubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import SubSubSubSectionParser

WIKI_LAYOUT_CASES = [
    pytest.param("old", "wiki_layout_old_html", id="layout-old"),
    pytest.param("new", "wiki_layout_new_html", id="layout-new"),
]


def _assert_table_contract(table_data: dict[str, object]) -> None:
    headers = table_data.get("headers")
    rows = table_data.get("rows")

    assert isinstance(headers, list)
    assert isinstance(rows, list)
    assert headers, "Table parser must expose at least one header"
    assert all(isinstance(header, str) and header.strip() for header in headers)

    for row in rows:
        assert isinstance(row, list)
        assert len(row) == len(headers)
        for cell in row:
            assert isinstance(cell, str)
            assert "\x00" not in cell


def _assert_article_table_contract(table_data: dict[str, object]) -> None:
    headers = table_data.get("headers")
    rows = table_data.get("rows")

    assert isinstance(headers, list)
    assert isinstance(rows, list)
    assert headers
    assert all(isinstance(header, str) and header.strip() for header in headers)

    for row in rows:
        assert isinstance(row, dict)
        assert set(row.keys()).issubset(set(headers))
        assert set(row.keys()) == set(headers)
        for value in row.values():
            assert isinstance(value, str)
            assert "\x00" not in value


@pytest.mark.parametrize("_layout,fixture_name", WIKI_LAYOUT_CASES)
def test_wiki_element_parsers_contract_stable_types(request, _layout: str, fixture_name: str) -> None:
    html = request.getfixturevalue(fixture_name)
    soup = BeautifulSoup(html, "html.parser")

    parser_cases = [
        (HeaderParser(), soup.find("header"), dict),
        (BodyContentParser(), soup.find("div", id="bodyContent"), dict),
        (CategoryLinksParser(), soup.find("div", id="catlinks"), dict),
        (ContentTextParser(), soup.find("div", class_="mw-content-ltr"), dict),
        (InfoboxParser(), soup.find("table", class_="infobox"), dict),
        (ParagraphParser(), soup.find("p"), dict),
        (FigureParser(), soup.find("figure"), dict),
        (ListParser(), soup.find("ul", class_="sample-list"), dict),
        (TableParser(), soup.find("table", class_="wikitable"), dict),
        (NavBoxParser(), soup.find("div", class_="navbox"), dict),
        (ReferencesWrapParser(), soup.find("div", class_="references-wrap"), dict),
        (ArticleTablesParser(), soup.find("div", id="bodyContent"), list),
        (SectionParser(), soup.find("div", class_="mw-content-ltr"), dict),
        (SubSectionParser(), soup.find("div", class_="mw-content-ltr"), dict),
        (SubSubSectionParser(), soup.find("div", class_="mw-content-ltr"), dict),
        (SubSubSubSectionParser(), soup.find("div", class_="mw-content-ltr"), dict),
    ]

    for parser, element, expected_type in parser_cases:
        assert isinstance(element, Tag)
        result = parser.parse(element)
        assert isinstance(result, expected_type)


@pytest.mark.parametrize("_layout,fixture_name", WIKI_LAYOUT_CASES)
def test_wiki_element_dispatcher_ignores_unsupported_nodes(request, _layout: str, fixture_name: str) -> None:
    html = request.getfixturevalue(fixture_name)
    soup = BeautifulSoup(html, "html.parser")
    parser = SubSubSubSectionParser()

    unsupported = soup.find("aside", attrs={"data-unsupported": "1"})
    assert isinstance(unsupported, Tag)

    result = parser.parse_elements([unsupported])

    assert result == []


@pytest.mark.parametrize("_layout,fixture_name", WIKI_LAYOUT_CASES)
def test_wiki_table_contract_for_layout_variants(request, _layout: str, fixture_name: str) -> None:
    html = request.getfixturevalue(fixture_name)
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table", class_="wikitable")
    assert isinstance(table, Tag)

    table_data = TableParser().parse(table)

    _assert_table_contract(table_data)


@pytest.mark.parametrize("_layout,fixture_name", WIKI_LAYOUT_CASES)
def test_article_tables_contract_for_layout_variants(request, _layout: str, fixture_name: str) -> None:
    html = request.getfixturevalue(fixture_name)
    soup = BeautifulSoup(html, "html.parser")

    body_content = soup.find("div", id="bodyContent")
    assert isinstance(body_content, Tag)

    tables = ArticleTablesParser().parse(body_content)

    assert isinstance(tables, list)
    assert tables
    for table_data in tables:
        assert isinstance(table_data, dict)
        _assert_article_table_contract(table_data)
