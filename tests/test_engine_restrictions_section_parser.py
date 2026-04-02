from scrapers.engines.engine_restrictions import CurrentRulesSectionParser
from scrapers.engines.engine_restrictions import EngineRestrictionsTableParser
from scrapers.engines.engine_restrictions import EngineSubSectionParser


def test_engine_restrictions_parser_chain_is_wired() -> None:
    parser = CurrentRulesSectionParser()

    assert isinstance(parser.child_parser, EngineSubSectionParser)
    assert isinstance(parser.child_parser._table_parser, EngineRestrictionsTableParser)


def test_engine_restrictions_table_parser_maps_headers() -> None:
    parser = EngineRestrictionsTableParser()
    table = {
        "headers": ["Year", "2000-2005", "2006-2013", "2014-2025"],
        "rows": [
            {
                "Year": "Size",
                "2000-2005": "3.0 L",
                "2006-2013": "2.4 L",
                "2014-2025": "1.6 L",
            },
        ],
    }

    parsed = parser.parse(table)

    assert parsed is not None
    assert parsed["table_type"] == "engine_restrictions"
    assert parsed["domain_column_map"]["Year"] == "year"
    assert parsed["domain_rows"][0]["rules_2014_2025"] == "1.6 L"
