"""Base scraper for constructor list pages."""

from collections.abc import Sequence

from scrapers.base.mixins.section_table_parse import DeclarativeSectionTableParseMixin
from scrapers.base.options import ScraperOptions
from scrapers.base.table.builders import EntityColumnSpec
from scrapers.base.table.builders import build_base_stats_columns
from scrapers.base.table.builders import build_columns
from scrapers.base.table.builders import build_entity_metadata_columns
from scrapers.base.table.columns.types import AutoColumn
from scrapers.base.table.columns.types import IntColumn
from scrapers.base.table.columns.types import LinksListColumn
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.base.table.seed_list_scraper import SeedListTableScraper
from scrapers.constructors.constants import CONSTRUCTOR_DRIVERS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_NAME_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_TOTAL_ENTRIES_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_WCC_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_WDC_HEADER


class BaseConstructorListScraper(
    DeclarativeSectionTableParseMixin,
    SeedListTableScraper,
):
    domain = "constructors"
    output_basename = "complete_constructors"
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
        return build_entity_metadata_columns(
            [
                EntityColumnSpec(CONSTRUCTOR_NAME_HEADER, "constructor", AutoColumn()),
                EntityColumnSpec(CONSTRUCTOR_DRIVERS_HEADER, "drivers", IntColumn()),
                EntityColumnSpec(
                    CONSTRUCTOR_TOTAL_ENTRIES_HEADER,
                    "total_entries",
                    IntColumn(),
                ),
                EntityColumnSpec(CONSTRUCTOR_WCC_HEADER, "wcc_titles", IntColumn()),
                EntityColumnSpec(CONSTRUCTOR_WDC_HEADER, "wdc_titles", IntColumn()),
            ],
        )

    @staticmethod
    def build_licensed_in_ColumnSpec():
        """Build the licensed_in column definition."""
        from scrapers.constructors.constants import CONSTRUCTOR_LICENSED_IN_HEADER

        return ColumnSpec(CONSTRUCTOR_LICENSED_IN_HEADER, "licensed_in", LinksListColumn())

    @classmethod
    def extend_schema_fragments(
        cls,
        fragments: Sequence[Sequence[ColumnSpec]],
    ) -> Sequence[Sequence[ColumnSpec]]:
        """Hook for domain-specific schema fragment customization."""
        return fragments

    @classmethod
    def build_schema_columns(
        cls,
        *fragments: Sequence[ColumnSpec],
    ) -> list[ColumnSpec]:
        resolved_fragments = cls.extend_schema_fragments(list(fragments))
        return build_columns(*resolved_fragments)

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config=None,
    ) -> None:
        options = options or ScraperOptions()
        options.normalize_empty_values = False
        super().__init__(options=options, config=config)
