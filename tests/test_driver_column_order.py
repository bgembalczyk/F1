from scrapers.constants_drivers import DRIVER_NAME_HEADER
from scrapers.constants_drivers import DRIVER_POINTS_HEADER
from scrapers.constants_drivers import DRIVER_RACE_WINS_HEADER
from scrapers.constants_drivers import FATALITIES_AGE_HEADER
from scrapers.constants_drivers import FATALITIES_DATE_HEADER
from scrapers.constants_drivers import FATALITIES_DRIVER_HEADER
from scrapers.drivers.fatalities_list_scraper_drivers import FatalitiesTableParser
from scrapers.drivers.list_scraper_drivers import DriversListTableParser
from scrapers.drivers.constants_drivers import DRIVER_NAME_HEADER
from scrapers.drivers.constants_drivers import DRIVER_POINTS_HEADER
from scrapers.drivers.constants_drivers import DRIVER_RACE_WINS_HEADER
from scrapers.drivers.constants_drivers import FATALITIES_AGE_HEADER
from scrapers.drivers.constants_drivers import FATALITIES_DATE_HEADER
from scrapers.drivers.constants_drivers import FATALITIES_DRIVER_HEADER
from scrapers.drivers.fatalities_list_scraper_drivers import FatalitiesTableMapper
from scrapers.drivers.list_scraper_drivers import DriversListTableMapper


def test_drivers_list_table_parser_places_driver_mapping_first() -> None:
    parser = DriversListTableMapper()

    result = parser.map_columns(
        [
            DRIVER_POINTS_HEADER,
            DRIVER_NAME_HEADER,
            DRIVER_RACE_WINS_HEADER,
        ],
    )

    assert next(iter(result.values())) == "driver"
    assert next(iter(result.keys())) == DRIVER_NAME_HEADER


def test_fatalities_table_parser_places_driver_mapping_first() -> None:
    parser = FatalitiesTableMapper()

    result = parser.map_columns(
        [
            FATALITIES_AGE_HEADER,
            FATALITIES_DATE_HEADER,
            FATALITIES_DRIVER_HEADER,
        ],
    )

    assert next(iter(result.values())) == "driver"
    assert next(iter(result.keys())) == FATALITIES_DRIVER_HEADER
