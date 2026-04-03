from scrapers.engines.engine_regulation import EngineRegulationSubSectionParser
from scrapers.engines.engine_regulation import EngineRegulationTableParser
from scrapers.engines.engine_regulation import HistorySectionParser


def test_engine_regulation_table_parser_maps_domain_rows() -> None:
    parser = EngineRegulationTableParser()
    parsed = parser.parse(
        {
            "headers": [
                "Years",
                "Operating principle",
                "Maximum displacement - Naturally aspirated",
                "Maximum displacement - Forced induction",
                "Configuration",
                "RPM limit",
                "Fuel flow limit (Qmax)",
                "Fuel composition - Alcohol",
                "Fuel composition - Petrol",
            ],
            "rows": [
                {
                    "Years": "1950-1960",
                    "Operating principle": "Naturally aspirated",
                    "Maximum displacement - Naturally aspirated": "4.5 L",
                    "Maximum displacement - Forced induction": "1.5 L",
                    "Configuration": "Straight-8",
                    "RPM limit": "12000 rpm",
                    "Fuel flow limit (Qmax)": "N/A",
                    "Fuel composition - Alcohol": "Permitted",
                    "Fuel composition - Petrol": "Permitted",
                },
            ],
        },
    )

    assert parsed is not None
    assert parsed["table_type"] == "engine_regulation_progression"
    assert parsed["domain_rows"][0]["seasons"] == "1950-1960"


def test_history_section_parser_uses_engine_regulation_sub_section_parser() -> None:
    parser = HistorySectionParser()

    assert isinstance(parser.child_parser, EngineRegulationSubSectionParser)
