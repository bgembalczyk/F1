# ruff: noqa: SLF001


from scrapers.engines.engine_regulation import EngineRegulationSubSectionParser
from scrapers.engines.engine_regulation import EngineRegulationTableMapper


def test_engine_regulation_apply_for_elements_covers_all_guards() -> None:
    parser = EngineRegulationSubSectionParser()

    class _TableParserStub:
        def parse(self, data):
            if data.get("ok"):
                return {"parsed": True}
            return None

    parser._table_parser = _TableParserStub()
    elements = [
        {"kind": "text", "data": {"ok": True}},
        {"kind": "table", "data": "not-a-dict"},
        {"kind": "table", "data": {"ok": False}},
        {"kind": "table", "data": {"ok": True}},
    ]

    parser._apply_for_elements(elements)

    assert elements[0]["data"] == {"ok": True}
    assert elements[1]["data"] == "not-a-dict"
    assert elements[2]["data"] == {"ok": False}
    assert elements[3]["data"] == {"parsed": True}


def test_engine_regulation_apply_parser_recurses_nested_sections() -> None:
    parser = EngineRegulationSubSectionParser()
    parser._table_parser.parse = lambda data: {"mapped": data["id"]}

    payload = {
        "sub_sub_sections": [
            {
                "elements": [{"kind": "table", "data": {"id": "top"}}],
                "sub_sub_sections": [
                    {"elements": [{"kind": "table", "data": {"id": "inner"}}]},
                ],
            },
        ],
    }

    parser._apply_engine_regulation_table_parser(payload)

    top = payload["sub_sub_sections"][0]["elements"][0]["data"]
    inner = payload["sub_sub_sections"][0]["sub_sub_sections"][0]["elements"][0]["data"]
    assert top == {"mapped": "top"}
    assert inner == {"mapped": "inner"}


def test_engine_regulation_table_parser_matches_required_headers() -> None:
    parser = EngineRegulationTableMapper()
    assert parser.matches(["Years", "Operating principle", "Configuration"], {}) is True


def test_engine_regulation_table_parser_does_not_match_missing_headers() -> None:
    parser = EngineRegulationTableMapper()
    assert parser.matches(["Years", "Operating principle"], {}) is False
    assert parser.matches([], {}) is False


def test_engine_regulation_sub_section_parse_group_applies_parser() -> None:
    parser = EngineRegulationSubSectionParser()

    class _Stub:
        def parse(self, data):
            if data.get("match"):
                return {"table_type": "engine_regulation_progression"}
            return None

    parser._table_parser = _Stub()
    payload = {
        "sub_sub_sections": [
            {
                "elements": [{"kind": "table", "data": {"match": True}}],
                "sub_sub_sections": [],
            },
        ],
    }
    result = parser.parse_group(list(payload["sub_sub_sections"]), context=None)
    assert isinstance(result, dict)
