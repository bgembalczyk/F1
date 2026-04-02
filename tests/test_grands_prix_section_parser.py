from scrapers.grands_prix.list_scraper import ByRaceTitleSubSectionParser
from scrapers.grands_prix.list_scraper import GrandsPrixTableParser
from scrapers.grands_prix.list_scraper import RacesSectionParser


def test_grands_prix_table_parser_maps_domain_rows() -> None:
    parser = GrandsPrixTableParser()
    parsed = parser.parse(
        {
            "headers": ["Race title", "Country", "Years held", "Circuits", "Total"],
            "rows": [
                {
                    "Race title": "British Grand Prix",
                    "Country": "United Kingdom",
                    "Years held": "1926, 1948–present",
                    "Circuits": "4",
                    "Total": "78",
                },
            ],
        },
    )

    assert parsed is not None
    assert parsed["table_type"] == "grands_prix_list"
    assert parsed["domain_rows"][0]["race_title"] == "British Grand Prix"


def test_races_section_parser_uses_by_race_title_sub_section_parser() -> None:
    parser = RacesSectionParser()

    assert isinstance(parser.child_parser, ByRaceTitleSubSectionParser)
