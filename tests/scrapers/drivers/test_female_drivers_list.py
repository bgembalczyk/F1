# ruff: noqa: E501, PLR2004, SLF001
from scrapers.drivers.female_drivers_list import OfficialDriversSubSectionParser


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


def test_official_drivers_sub_section_parser_apply_female_recurses() -> None:
    parser = OfficialDriversSubSectionParser()
    payload = {
        "sub_sub_sections": [
            {
                "elements": [{"kind": "table", "data": {"id": "top"}}],
                "sub_sub_sections": [
                    {
                        "elements": [{"kind": "table", "data": {"id": "inner"}}],
                        "sub_sub_sections": [],
                    },
                ],
            },
        ],
    }

    class _Stub:
        def parse(self, data):
            return {"mapped": data["id"]}

    parser._table_parser = _Stub()
    parser._apply_female_drivers_table_parser(payload)

    assert payload["sub_sub_sections"][0]["elements"][0]["data"] == {"mapped": "top"}
    assert payload["sub_sub_sections"][0]["sub_sub_sections"][0]["elements"][0][
        "data"
    ] == {"mapped": "inner"}


def test_official_drivers_sub_section_parse_group_calls_apply_and_returns() -> None:
    parser = OfficialDriversSubSectionParser()

    class _Stub:
        def parse(self, _data):
            return None

    parser._table_parser = _Stub()
    result = parser.parse_group([], context=None)
    assert isinstance(result, dict)
