from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.parsers.input_adapters import as_dict_fragment
from scrapers.parsers.input_adapters import as_soup
from scrapers.parsers.input_adapters import as_table_fragments
from scrapers.parsers.input_adapters import as_tag
from scrapers.parsers.input_types import INPUT_TYPE_MAP
from scrapers.parsers.input_types import INPUT_TYPE_TO_CANONICAL
from scrapers.parsers.section.table.base import TableSectionParser
from scrapers.parsers.wiki.table.article import ArticleTablesParser


class _ContractSectionParser(TableSectionParser):
    def __init__(self) -> None:
        super().__init__(section_id="contract", section_label="Contract")

    def map_table_result(
        self,
        *,
        table_data: dict[str, object],
        table_classification: dict[str, object],
        table_pipeline: object,
    ) -> dict[str, object] | None:
        del table_data
        del table_pipeline
        return table_classification


def test_official_parser_input_type_mapping_contract() -> None:
    assert set(INPUT_TYPE_MAP) == {"tag", "soup", "dict_fragment"}
    assert {
        "tag": "soup",
        "soup": "soup",
        "dict_fragment": "dict_fragment",
    } == INPUT_TYPE_TO_CANONICAL


def test_parser_input_adapters_map_between_tag_soup_and_dict_fragment() -> None:
    soup = BeautifulSoup(
        "<table class='wikitable'><tr><th>A</th></tr></table>",
        "html.parser",
    )
    table = soup.find("table")
    assert table is not None

    assert as_tag(table) is table
    assert as_tag({"_table": table}) is table
    assert as_soup(soup) is soup
    assert as_soup(table).find("table") is not None
    assert as_dict_fragment(table) == {"_table": table}
    assert as_dict_fragment({"headers": ["A"]}) == {"headers": ["A"]}


def test_article_tables_parser_uses_uniform_dict_fragment_path() -> None:
    parser = ArticleTablesParser()
    fragment = {"headers": ["A"], "rows": [{"A": "1"}], "table_type": "wiki_table"}
    payload = {"tables": [fragment]}

    assert parser.parse(fragment) == [fragment]
    assert parser.parse(payload) == [fragment]
    assert as_table_fragments(payload) == [fragment]


def test_section_table_parser_base_accepts_soup_and_dict_fragments() -> None:
    parser = _ContractSectionParser()
    html = "<table class='wikitable'><tr><th>A</th></tr><tr><td>1</td></tr></table>"
    soup = BeautifulSoup(html, "html.parser")
    dict_payload = {"tables": [{"headers": ["A"], "rows": [{"A": "1"}]}]}

    soup_result = parser.parse(soup)
    dict_result = parser.parse(dict_payload)

    assert len(soup_result.records) == 1
    assert len(dict_result.records) == 1
    assert dict_result.records[0]["headers"] == ["A"]
