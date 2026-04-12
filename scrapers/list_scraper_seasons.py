from scrapers.adapters.factories.dataclass import RECORD_FACTORIES
from scrapers.builders_table import build_columns
from scrapers.columns.factory import IntColumn
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.links_list import LinksListColumn
from scrapers.columns.types.url import UrlColumn
from scrapers.config_table import TableScraperConfig
from scrapers.config_table import build_scraper_config
from scrapers.options import ScraperOptions
from scrapers.parsers.wiki.sections.seasons_list_section_parser import SeasonsSectionParser
from scrapers.seed_list_scraper_table import SeedListTableScraper
from scrapers.source_catalog import SEASONS_LIST
from scrapers.table_schema_dsl import TableSchemaDSL

TABLE_SCHEMA = TableSchemaDSL(
    columns=build_columns(
        ColumnSpec("Season", "season", UrlColumn()),
        ColumnSpec("Races", "races", IntColumn()),
        ColumnSpec("Countries", "countries", IntColumn()),
        ColumnSpec("First", "first", UrlColumn()),
        ColumnSpec("Last", "last", UrlColumn()),
        ColumnSpec(
            "Drivers' Champion (team)",
            "drivers_champion_team",
            LinksListColumn(),
        ),
        ColumnSpec(
            "Constructors' Champion",
            "constructors_champion",
            LinksListColumn(),
        ),
        ColumnSpec("Winners", "winners", IntColumn()),
    ),
)


class SeasonsListScraper(SeedListTableScraper):
    domain = "seasons"

    CONFIG = build_scraper_config(
        url=SEASONS_LIST.base_url,
        section_id=SEASONS_LIST.section_id,
        expected_headers=["Season", "Races"],
        schema=TABLE_SCHEMA,
        record_factory=RECORD_FACTORIES.builders("season_summary"),
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: TableScraperConfig | None = None,
    ) -> None:
        super().__init__(options=options, config=config)
        parser = SeasonsSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser


__all__ = ["SeasonsListScraper", "TABLE_SCHEMA"]
