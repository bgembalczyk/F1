"""Base scraper for constructor list pages."""

from collections.abc import Sequence

from scrapers.base.mixins.section_table_parse import DeclarativeSectionTableParseMixin
from scrapers.base.table.builders import EntityColumnSpec
from scrapers.base.table.builders import build_base_stats_columns
from scrapers.base.table.builders import build_columns
from scrapers.base.table.builders import build_entity_metadata_columns
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.column_factory import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.base.table.seed_list_scraper import SeedListTableScraper
from scrapers.constructors import constructors_constants


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
                EntityColumnSpec(
                    constructors_constants.CONSTRUCTOR_NAME_HEADER,
                    "constructor",
                    AutoColumn(),
                ),
                EntityColumnSpec(
                    constructors_constants.CONSTRUCTOR_DRIVERS_HEADER,
                    "drivers",
                    IntColumn(),
                ),
                EntityColumnSpec(
                    constructors_constants.CONSTRUCTOR_TOTAL_ENTRIES_HEADER,
                    "total_entries",
                    IntColumn(),
                ),
                EntityColumnSpec(
                    constructors_constants.CONSTRUCTOR_WCC_HEADER,
                    "wcc_titles",
                    IntColumn(),
                ),
                EntityColumnSpec(
                    constructors_constants.CONSTRUCTOR_WDC_HEADER,
                    "wdc_titles",
                    IntColumn(),
                ),
            ],
        )

    @staticmethod
    def build_licensed_in_column_spec() -> ColumnSpec:
        """Build the licensed_in column definition."""
        return ColumnSpec(
            constructors_constants.CONSTRUCTOR_LICENSED_IN_HEADER,
            "licensed_in",
            LinksListColumn(),
        )

    @staticmethod
    def build_licensed_in_ColumnSpec():  # noqa: N802
        """Backward-compatible alias for build_licensed_in_column_spec."""
        return BaseConstructorListScraper.build_licensed_in_column_spec()

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




__all__ = ["BaseConstructorListScraper"]
