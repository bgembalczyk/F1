"""Base scraper for constructor list pages."""

from scrapers.base.mixins.section_table_parse import DeclarativeSectionTableParseMixin
from scrapers.base.options import ScraperOptions
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.presets import BASE_STATS_COLUMNS
from scrapers.base.table.presets import BASE_STATS_MAP
from scrapers.base.table.scraper import F1TableScraper
from scrapers.constructors.constants import CONSTRUCTOR_DRIVERS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_NAME_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_TOTAL_ENTRIES_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_WCC_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_WDC_HEADER


class BaseConstructorListScraper(DeclarativeSectionTableParseMixin, F1TableScraper):
    domain = "constructors"
    """
    Base class for constructor list scrapers.

    Provides common column definitions for scraping constructor data from Wikipedia,
    following DRY principles by centralizing shared schema definitions.

    Subclasses should define their own CONFIG with specific:
    - url
    - section_id
    - expected_headers
    - schema (can use build_common_stats_columns helper)
    - record_factory
    """

    @staticmethod
    def build_common_stats_columns():
        """
        Build common statistics columns used across constructor list tables.

        Returns list of column definitions for standard statistics fields
        like seasons, races, wins, points, etc.
        """
        return [
            column(
                header,
                {"wcc": "wcc_titles", "wdc": "wdc_titles"}.get(key, key),
                BASE_STATS_COLUMNS[key],
            )
            for header, key in BASE_STATS_MAP.items()
        ]

    @staticmethod
    def build_common_metadata_columns():
        """
        Build common metadata columns used across constructor list tables.

        Returns list of column definitions for metadata fields like
        constructor name, drivers count, total entries, and championship titles.
        """
        return [
            column(CONSTRUCTOR_NAME_HEADER, "constructor", UrlColumn()),
            column(CONSTRUCTOR_DRIVERS_HEADER, "drivers", IntColumn()),
            column(CONSTRUCTOR_TOTAL_ENTRIES_HEADER, "total_entries", IntColumn()),
            column(CONSTRUCTOR_WCC_HEADER, "wcc_titles", IntColumn()),
            column(CONSTRUCTOR_WDC_HEADER, "wdc_titles", IntColumn()),
        ]

    @staticmethod
    def build_licensed_in_column():
        """Build the licensed_in column definition."""
        from scrapers.constructors.constants import CONSTRUCTOR_LICENSED_IN_HEADER

        return column(CONSTRUCTOR_LICENSED_IN_HEADER, "licensed_in", LinksListColumn())

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config=None,
    ) -> None:
        options = options or ScraperOptions()
        options.normalize_empty_values = False
        super().__init__(options=options, config=config)
