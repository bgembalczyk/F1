from scrapers.drivers.constants import DRIVER_NAME_HEADER
from scrapers.drivers.constants import DRIVER_POINTS_HEADER
from scrapers.drivers.constants import DRIVER_RACE_WINS_HEADER
from scrapers.drivers.constants import FATALITIES_AGE_HEADER
from scrapers.drivers.constants import FATALITIES_DATE_HEADER
from scrapers.drivers.constants import FATALITIES_DRIVER_HEADER
from scrapers.drivers.fatalities_list_scraper import FatalitiesTableParser
from scrapers.drivers.list_scraper import DriversListTableParser


def test_drivers_list_table_parser_places_driver_mapping_first() -> None:
    parser = DriversListTableParser()

    result = parser.map_columns(
        [
            DRIVER_POINTS_HEADER,
            DRIVER_NAME_HEADER,
            DRIVER_RACE_WINS_HEADER,
        ],
    )

    assert list(result.values())[0] == "driver"
    assert list(result.keys())[0] == DRIVER_NAME_HEADER


def test_fatalities_table_parser_places_driver_mapping_first() -> None:
    parser = FatalitiesTableParser()

    result = parser.map_columns(
        [
            FATALITIES_AGE_HEADER,
            FATALITIES_DATE_HEADER,
            FATALITIES_DRIVER_HEADER,
        ],
    )

    assert list(result.values())[0] == "driver"
    assert list(result.keys())[0] == FATALITIES_DRIVER_HEADER
