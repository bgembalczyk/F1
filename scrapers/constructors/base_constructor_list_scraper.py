"""Base scraper for constructor list pages."""

from scrapers.base.mixins.section_table_parse import DeclarativeSectionTableParseMixin
from scrapers.base.table.builders import build_base_stats_columns
from scrapers.base.table.builders import build_columns
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.seed_list_scraper import BaseSeedListScraper
from scrapers.constructors.constants import CONSTRUCTOR_DRIVERS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_LICENSED_IN_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_NAME_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_TOTAL_ENTRIES_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_WCC_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_WDC_HEADER


class BaseConstructorListScraper(
    DeclarativeSectionTableParseMixin,
    BaseSeedListScraper,
):
    domain = "constructors"
    default_output_path = "raw/constructors/seeds/complete_constructors"
    legacy_output_path = "constructors/complete_constructors"
    normalize_empty_values = False
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
        """Build common constructor statistics columns."""
        return build_base_stats_columns(
            key_aliases={"wcc": "wcc_titles", "wdc": "wdc_titles"},
        )

    @staticmethod
    def build_common_metadata_columns():
        """Build common constructor metadata columns."""
        return build_columns(
            column(CONSTRUCTOR_NAME_HEADER, "constructor", UrlColumn()),
            column(CONSTRUCTOR_DRIVERS_HEADER, "drivers", IntColumn()),
            column(CONSTRUCTOR_TOTAL_ENTRIES_HEADER, "total_entries", IntColumn()),
            column(CONSTRUCTOR_WCC_HEADER, "wcc_titles", IntColumn()),
            column(CONSTRUCTOR_WDC_HEADER, "wdc_titles", IntColumn()),
        )

    @staticmethod
    def build_licensed_in_column():
        """Build the licensed_in column definition."""
        return column(CONSTRUCTOR_LICENSED_IN_HEADER, "licensed_in", LinksListColumn())
