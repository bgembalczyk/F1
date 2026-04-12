# ruff: noqa: E501, PLR2004, SLF001
from scrapers.parsers.section.legacy_lists.female_drivers import OfficialDriversSubSectionParser


def test_official_drivers_sub_section_parser_apply_for_elements_skips_non_table() -> (
    None
):
    parser = OfficialDriversSubSectionParser()
    elements = [
        {"kind": "text", "data": {"should": "remain"}},
        {"kind": "table", "data": "not-a-dict"},
    ]

    class _Stub:
        def parse(self, _data):
            return None

    parser._table_parser = _Stub()
    parser._apply_for_elements(elements)

    assert elements[0]["data"] == {"should": "remain"}
    assert elements[1]["data"] == "not-a-dict"


def test_official_drivers_sub_section_parser_apply_for_elements_replaces_matched_table() -> (
    None
):
    parser = OfficialDriversSubSectionParser()
    elements = [{"kind": "table", "data": {"ok": True}}]

    class _Stub:
        def parse(self, _data):
            return {"table_type": "female_drivers_list"}

    parser._table_parser = _Stub()
    parser._apply_for_elements(elements)
    assert elements[0]["data"] == {"table_type": "female_drivers_list"}


def test_official_drivers_sub_section_parse_group_calls_apply_and_returns() -> None:
    parser = OfficialDriversSubSectionParser()

    class _Stub:
        def parse(self, _data):
            return None

    parser._table_parser = _Stub()
    result = parser.parse_group([], context=None)
    assert isinstance(result, dict)
