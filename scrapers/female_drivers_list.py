from scrapers.adapters.factories.dataclass import RECORD_FACTORIES
from scrapers.config_table import build_scraper_config
from scrapers.constants.constants_drivers import FEMALE_DRIVERS_HEADERS
from scrapers.constants.constants_drivers import FEMALE_DRIVERS_SECTION_ID
from scrapers.options import ScraperOptions
from scrapers.parsers.section.legacy_lists.female_drivers import DriversSectionParser
from scrapers.parsers.section.legacy_lists.female_drivers import (
    FemaleDriversTableMapper,
)
from scrapers.parsers.section.legacy_lists.female_drivers import (
    OfficialDriversSubSectionParser,
)
from scrapers.scraper_table import F1TableScraper
from scrapers.source_catalog import FEMALE_DRIVERS_LIST


class FemaleDriversListScraper(F1TableScraper):
    """
    Scraper listy oficjalnych kobiet-kierowców F1 z:
    https://en.wikipedia.org/wiki/List_of_female_Formula_One_drivers
    """

    options_profile = "seed_soft"

    CONFIG = build_scraper_config(
        url=FEMALE_DRIVERS_LIST.base_url,
        section_id=FEMALE_DRIVERS_SECTION_ID,
        expected_headers=FEMALE_DRIVERS_HEADERS,
        schema=FemaleDriversTableMapper.build_schema(),
        record_factory=RECORD_FACTORIES.builders("special_driver"),
    )

    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        super().__init__(options=options)
        parser = DriversSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser


FemaleDriversTableParser = FemaleDriversTableMapper

__all__ = [
    "DriversSectionParser",
    "FemaleDriversListScraper",
    "FemaleDriversTableMapper",
    "FemaleDriversTableParser",
    "OfficialDriversSubSectionParser",
]
