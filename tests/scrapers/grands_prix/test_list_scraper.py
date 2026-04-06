# ruff: noqa: E501, PLR2004, SLF001
from scrapers.grands_prix.list_scraper import ByRaceTitleSubSectionParser, GrandsPrixTableParser


def test_grands_prix_table_parser_matches_required_headers() -> None:
    parser = GrandsPrixTableParser()
    assert parser.matches(["Race title", "Years held"], {}) is True
    assert parser.matches(["Race title", "Years held", "Extra"], {}) is True


def test_grands_prix_table_parser_does_not_match_missing_headers() -> None:
    parser = GrandsPrixTableParser()
    assert parser.matches(["Race title"], {}) is False
    assert parser.matches([], {}) is False


def test_grands_prix_table_parser_map_columns_filters_known() -> None:
    parser = GrandsPrixTableParser()
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
        def parse(self, data):
            return None

    parser._table_parser = _Stub()
    parser._apply_for_elements(elements)
    assert elements[0]["data"] == {"preserve": True}
    assert elements[1]["data"] == "not-a-dict"


def test_by_race_title_sub_section_parser_apply_for_elements_replaces_matched() -> None:
    parser = ByRaceTitleSubSectionParser()
    elements = [{"kind": "table", "data": {"ok": True}}]

    class _Stub:
        def parse(self, data):
            return {"table_type": "grands_prix_list"}

    parser._table_parser = _Stub()
    parser._apply_for_elements(elements)
    assert elements[0]["data"] == {"table_type": "grands_prix_list"}


def test_by_race_title_sub_section_parser_apply_table_parser_recurses() -> None:
    parser = ByRaceTitleSubSectionParser()
    payload = {
        "sub_sub_sections": [
            {
                "elements": [{"kind": "table", "data": {"id": "top"}}],
                "sub_sub_sections": [
                    {"elements": [{"kind": "table", "data": {"id": "inner"}}], "sub_sub_sections": []},
                ],
            },
        ],
    }

    class _Stub:
        def parse(self, data):
            return {"mapped": data["id"]}

    parser._table_parser = _Stub()
    parser._apply_table_parser(payload)

    assert payload["sub_sub_sections"][0]["elements"][0]["data"] == {"mapped": "top"}
    assert payload["sub_sub_sections"][0]["sub_sub_sections"][0]["elements"][0]["data"] == {"mapped": "inner"}


def test_by_race_title_parse_group_returns_dict() -> None:
    parser = ByRaceTitleSubSectionParser()

    class _Stub:
        def parse(self, data):
            return None

    parser._table_parser = _Stub()
    result = parser.parse_group([], context=None)
    assert isinstance(result, dict)
