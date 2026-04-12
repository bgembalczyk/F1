from models.records.factories.mapping import MappingRecordFactory
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.append_links import AppendLinksColumn
from scrapers.columns.types.seasons import SeasonsColumn
from scrapers.columns.types.skip import SkipColumn
from scrapers.config_table import TableConfig
from scrapers.config_table import build_scraper_config
from scrapers.options import ScraperOptions
from scrapers.parsers.section.legacy_lists.tyres import ManufacturersSectionParser
from scrapers.parsers.section.legacy_lists.tyres import TyreManufacturersBySeasonSubSectionParser
from scrapers.parsers.section.legacy_lists.tyres import TyreManufacturersBySeasonTableMapper
from scrapers.scraper_table import F1TableScraper
from scrapers.source_catalog import TYRES
from scrapers.table_schema_dsl import TableSchemaDSL

TABLE_SCHEMA = TableSchemaDSL(
    columns=[
        ColumnSpec("Season", "seasons", SeasonsColumn()),
        ColumnSpec("Manufacturer 1", "manufacturers", AppendLinksColumn()),
        ColumnSpec("Manufacturer 2", "manufacturers", AppendLinksColumn()),
        ColumnSpec("Manufacturer 3", "manufacturers", AppendLinksColumn()),
        ColumnSpec("Manufacturer 4", "manufacturers", AppendLinksColumn()),
        ColumnSpec("Manufacturer 5", "manufacturers", AppendLinksColumn()),
        ColumnSpec("Manufacturer 6", "manufacturers", AppendLinksColumn()),
        ColumnSpec("Wins", "wins", SkipColumn()),
    ],
)


class TyreManufacturersScraper(F1TableScraper):
    """
    Scraper producentów opon F1:
    https://en.wikipedia.org/wiki/Formula_One_tyres#Tyre_manufacturers_by_season
    """

    CONFIG = build_scraper_config(
        url=TYRES.url(),
        section_id=TYRES.section_id,
        expected_headers=[
            "Season",
            "Manufacturer 1",
            "Wins",
        ],
        schema=TABLE_SCHEMA,
        record_factory=MappingRecordFactory(),
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: TableConfig | None = None,
    ) -> None:
        super().__init__(options=options, config=config)
        parser = ManufacturersSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser


TyreManufacturersBySeasonTableParser = TyreManufacturersBySeasonTableMapper

__all__ = [
    "ManufacturersSectionParser",
    "TyreManufacturersBySeasonSubSectionParser",
    "TyreManufacturersBySeasonTableMapper",
    "TyreManufacturersBySeasonTableParser",
    "TyreManufacturersScraper",
]
