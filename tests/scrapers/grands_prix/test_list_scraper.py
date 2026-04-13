# ruff: noqa: E501, PLR2004, SLF001
from scrapers.parsers.section.legacy_lists.grands_prix import (
    ByRaceTitleSubSectionParser,
)
from scrapers.parsers.section.legacy_lists.grands_prix import GrandsPrixTableMapper


def test_grands_prix_table_parser_matches_required_headers() -> None:
    parser = GrandsPrixTableMapper()
    assert parser.matches(["Race title", "Years held"], {}) is True
    assert parser.matches(["Race title", "Years held", "Extra"], {}) is True


def test_grands_prix_table_parser_does_not_match_missing_headers() -> None:
    parser = GrandsPrixTableMapper()
    assert parser.matches(["Race title"], {}) is False
    assert parser.matches([], {}) is False


def test_grands_prix_table_parser_map_columns_filters_known() -> None:
    parser = GrandsPrixTableMapper()
    result = parser.map_columns(["Race title", "Years held", "Unknown"])
    assert "Race title" in result
    assert "Years held" in result
    assert "Unknown" not in result


def test_by_race_title_sub_section_parser_apply_for_elements_skips_non_table() -> None:
    parser = ByRaceTitleSubSectionParser()
    elements = [
        {"kind": "text", "data": {"preserve": True}},
        {"kind": "table", "data": "not-a-dict"},
    ]

    class _Stub:
        def parse(self, _data):
            return None

    parser._table_parser = _Stub()
    parser._apply_for_elements(elements)
    assert elements[0]["data"] == {"preserve": True}
    assert elements[1]["data"] == "not-a-dict"


def test_by_race_title_sub_section_parser_apply_for_elements_replaces_matched() -> None:
    parser = ByRaceTitleSubSectionParser()
    elements = [{"kind": "table", "data": {"ok": True}}]

    class _Stub:
        def parse(self, _data):
            return {"table_type": "grands_prix_list"}

    parser._table_parser = _Stub()
    parser._apply_for_elements(elements)
    assert elements[0]["data"] == {"table_type": "grands_prix_list"}


def test_by_race_title_parse_group_returns_dict() -> None:
    parser = ByRaceTitleSubSectionParser()

    class _Stub:
        def apply_to_payload(self, _payload):
            pass

    parser._table_parser = _Stub()
    result = parser.parse_group([], context=None)
    assert isinstance(result, dict)
