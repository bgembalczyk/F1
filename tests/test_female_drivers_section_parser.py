from scrapers.drivers.female_drivers_list import DriversSectionParser
from scrapers.drivers.female_drivers_list import FemaleDriversTableParser
from scrapers.drivers.female_drivers_list import OfficialDriversSubSectionParser


def test_female_drivers_table_parser_maps_domain_rows() -> None:
    parser = FemaleDriversTableParser()
    parsed = parser.parse(
        {
            "headers": [
                "#",
                "Name",
                "Seasons",
                "Teams",
                "Entries (starts)",
                "Points",
            ],
            "rows": [
                {
                    "#": "1",
                    "Name": "Maria Teresa de Filippis",
                    "Seasons": "1958",
                    "Teams": "Maserati",
                    "Entries (starts)": "5/3",
                    "Points": "0",
                },
            ],
        },
    )

    assert parsed is not None
    assert parsed["table_type"] == "female_drivers_list"
    assert parsed["domain_rows"][0]["driver"] == "Maria Teresa de Filippis"


def test_drivers_section_parser_uses_official_sub_section_parser() -> None:
    parser = DriversSectionParser()

    assert isinstance(parser.child_parser, OfficialDriversSubSectionParser)
