"""DEPRECATED ENTRYPOINT: use scrapers.grands_prix.entrypoint.run_list_scraper."""

from __future__ import annotations

import warnings

from scrapers.adapters.factories.dataclass import RECORD_FACTORIES
from scrapers.builders_table import build_columns
from scrapers.builders_table import build_entity_metadata_columns
from scrapers.builders_table import build_name_status_fragment
from scrapers.columns.entity_column_spec import EntityColumnSpec
from scrapers.columns.factory import IntColumn
from scrapers.columns.types.links_list import LinksListColumn
from scrapers.columns.types.multi.name_status_column.race_title_status import (
    RaceTitleStatusColumn,
)
from scrapers.columns.types.seasons import SeasonsColumn
from scrapers.config_table import build_scraper_config
from scrapers.options import ScraperOptions
from scrapers.parsers.section.legacy_lists.grands_prix import (
    ByRaceTitleSubSectionParser,
)
from scrapers.parsers.section.legacy_lists.grands_prix import GrandsPrixTableMapper
from scrapers.parsers.section.legacy_lists.grands_prix import RacesSectionParser
from scrapers.seed_list_scraper_table import SeedListTableScraper
from scrapers.source_catalog import GRANDS_PRIX_LIST
from scrapers.table_schema_dsl import TableSchemaDSL

warnings.warn(
    "list_scraper_grands_prix is deprecated; use scrapers.grands_prix_list_scraper.",
    DeprecationWarning,
    stacklevel=2,
)

TABLE_SCHEMA = TableSchemaDSL(
    columns=build_columns(
        build_name_status_fragment(
            header="Race title",
            output_key="race_title",
            column_type=RaceTitleStatusColumn(),
        ),
        build_entity_metadata_columns(
            [
                EntityColumnSpec("Country", "country", LinksListColumn()),
                EntityColumnSpec("Years held", "years_held", SeasonsColumn()),
                EntityColumnSpec("Circuits", "circuits", IntColumn()),
                EntityColumnSpec("Total", "total", IntColumn()),
            ],
        ),
    ),
)


class GrandsPrixListScraper(SeedListTableScraper):
    domain = "grands_prix"
    output_basename = "f1_grands_prix_extended.json"

    """
    Uproszczony scraper np. dla tabeli 'By race title'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix
    """

    CONFIG = build_scraper_config(
        url=GRANDS_PRIX_LIST.base_url,
        section_id=GRANDS_PRIX_LIST.section_id,
        expected_headers=[
            "Race title",
            "Years held",
        ],
        schema=TABLE_SCHEMA,
        record_factory=RECORD_FACTORIES.builders("grands_prix"),
    )

    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        super().__init__(options=options)
        parser = RacesSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser


GrandsPrixTableParser = GrandsPrixTableMapper

__all__ = [
    "ByRaceTitleSubSectionParser",
    "GrandsPrixListScraper",
    "GrandsPrixTableMapper",
    "GrandsPrixTableParser",
    "RacesSectionParser",
]
