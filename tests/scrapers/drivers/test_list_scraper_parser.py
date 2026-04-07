# ruff: noqa: E501, PLR2004, SLF001
from scrapers.drivers.constants import DRIVERS_LIST_HEADERS
from scrapers.drivers.list_scraper import DriversListSectionParser
from scrapers.drivers.list_scraper import DriversListTableParser


def test_drivers_list_table_parser_matches_when_all_required_headers_present() -> None:
    parser = DriversListTableParser()
    assert parser.matches(list(DRIVERS_LIST_HEADERS), {}) is True


def test_drivers_list_table_parser_does_not_match_with_missing_headers() -> None:
    parser = DriversListTableParser()
    assert parser.matches(["Driver name"], {}) is False


def test_drivers_list_table_parser_matches_with_extra_headers() -> None:
    parser = DriversListTableParser()
    headers = [*list(DRIVERS_LIST_HEADERS), "Extra column"]
    assert parser.matches(headers, {}) is True


def test_drivers_list_section_parser_parse_group_calls_apply() -> None:
    parser = DriversListSectionParser()
    payload = {
        "sub_sections": [
            {
                "elements": [
                    {"kind": "table", "data": {"ok": True}},
                ],
                "sub_sections": [],
            },
        ],
    }

    class _Stub:
        def parse(self, data):
            if data.get("ok"):
                return {"table_type": "drivers_list", "domain_rows": []}
            return None

    parser._table_parser = _Stub()
    result = parser.parse_group(payload["sub_sections"][0]["elements"])
    assert result is not None


def test_drivers_list_section_parser_apply_for_elements_skips_non_table() -> None:
    parser = DriversListSectionParser()
    elements = [
        {"kind": "text", "data": {"should": "remain"}},
        {"kind": "table", "data": "not-a-dict"},
        {"kind": "table", "data": {"ok": False}},
    ]

    class _Stub:
        def parse(self, data):
            return None

    parser._table_parser = _Stub()
    parser._apply_for_elements(elements)

    assert elements[0]["data"] == {"should": "remain"}
    assert elements[1]["data"] == "not-a-dict"


def test_drivers_list_section_parser_apply_for_elements_replaces_on_match() -> None:
    parser = DriversListSectionParser()
    elements = [{"kind": "table", "data": {"ok": True}}]

    class _Stub:
        def parse(self, data):
            return {"table_type": "drivers_list"}

    parser._table_parser = _Stub()
    parser._apply_for_elements(elements)
    assert elements[0]["data"] == {"table_type": "drivers_list"}


def test_drivers_list_section_parser_apply_recurses() -> None:
    parser = DriversListSectionParser()
    payload = {
        "sub_sections": [
            {
                "elements": [{"kind": "table", "data": {"id": "top"}}],
                "sub_sections": [
                    {
                        "elements": [{"kind": "table", "data": {"id": "inner"}}],
                        "sub_sections": [],
                    },
                ],
            },
        ],
    }

    class _Stub:
        def parse(self, data):
            return {"mapped": data["id"]}

    parser._table_parser = _Stub()
    parser._apply_drivers_table_parser(payload)

    assert payload["sub_sections"][0]["elements"][0]["data"] == {"mapped": "top"}
    assert payload["sub_sections"][0]["sub_sections"][0]["elements"][0]["data"] == {
        "mapped": "inner",
    }
