from typing import Any

from models.records.factories.mapping import MappingRecordFactory
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.append_links import AppendLinksColumn
from scrapers.columns.types.seasons import SeasonsColumn
from scrapers.columns.types.skip import SkipColumn
from scrapers.config_table import TableScraperConfig
from scrapers.config_table import build_scraper_config
from scrapers.options import ScraperOptions
from scrapers.parsers.section.protocol import SectionParser
from scrapers.parsers.table.wiki.base import WikiTableBaseMapper
from scrapers.parsers.table.table.base import WikiTableBaseParser
from scrapers.parsers.wiki.sublevels.sub_section import SubSectionParser
from scrapers.scraper_table import F1TableScraper
from scrapers.source_catalog import TYRES
from scrapers.table_schema_dsl import TableSchemaDSL


class TyreManufacturersBySeasonTableMapper(WikiTableBaseMapper):
    table_type = "tyre_manufacturers_by_season"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Season": "seasons",
        "Manufacturer 1": "manufacturers",
        "Manufacturer 2": "manufacturers",
        "Manufacturer 3": "manufacturers",
        "Manufacturer 4": "manufacturers",
        "Manufacturer 5": "manufacturers",
        "Manufacturer 6": "manufacturers",
        "Wins": "wins",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {"Season", "Manufacturer 1", "Wins"}
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }


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


class TyreManufacturersBySeasonSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = TyreManufacturersBySeasonTableMapper()

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self._table_parser.apply_to_payload(parsed)
        return parsed


class ManufacturersSectionParser(SectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = TyreManufacturersBySeasonSubSectionParser()


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
        config: TableScraperConfig | None = None,
    ) -> None:
        super().__init__(options=options, config=config)
        parser = ManufacturersSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser
