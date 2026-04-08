from typing import Any

from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.mixins.apply_for_elements import ApplyForElementsMixin
from scrapers.base.options import ScraperOptions
from scrapers.base.source_catalog import FEMALE_DRIVERS_LIST
from scrapers.base.table.columns import types as col
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.scraper import F1TableScraper
from scrapers.drivers.columns.entries_starts import EntriesStartsColumn
from scrapers.drivers import constants
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser


class FemaleDriversTableParser(WikiTableBaseParser):
    table_type = "female_drivers_list"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        constants.FEMALE_DRIVER_NAME_HEADER: "driver",
        constants.FEMALE_DRIVER_SEASONS_HEADER: "seasons",
        constants.FEMALE_DRIVER_TEAMS_HEADER: "teams",
        constants.FEMALE_DRIVER_ENTRIES_STARTS_HEADER: "entries_starts",
        constants.FEMALE_DRIVER_POINTS_HEADER: "points",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = set(constants.FEMALE_DRIVERS_HEADERS)
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }

    @staticmethod
    def build_schema() -> TableSchemaDSL:
        return TableSchemaDSL(
            columns=[
                ColumnSpec(constants.FEMALE_DRIVERS_INDEX_HEADER, "_skip", col.SkipColumn()),
                ColumnSpec(constants.FEMALE_DRIVER_NAME_HEADER, "driver", col.UrlColumn()),
                ColumnSpec(constants.FEMALE_DRIVER_SEASONS_HEADER, "seasons", col.SeasonsColumn()),
                ColumnSpec(constants.FEMALE_DRIVER_TEAMS_HEADER, "teams", col.LinksListColumn()),
                ColumnSpec(
                    constants.FEMALE_DRIVER_ENTRIES_STARTS_HEADER,
                    "entries_starts",
                    EntriesStartsColumn(),
                ),
                ColumnSpec(constants.FEMALE_DRIVER_POINTS_HEADER, "points", col.PointsColumn()),
            ],
        )


class OfficialDriversSubSectionParser(SubSectionParser, ApplyForElementsMixin):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = FemaleDriversTableParser()

    def parse_group(
        self,
        elements: list,
        *,
        context=None,
    ) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        self._apply_table_parser_to_sections(parsed, "sub_sub_sections")
        return parsed


class DriversSectionParser(SectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = OfficialDriversSubSectionParser()


class FemaleDriversListScraper(F1TableScraper):
    """
    Scraper listy oficjalnych kobiet-kierowców F1 z:
    https://en.wikipedia.org/wiki/List_of_female_Formula_One_drivers
    """

    options_profile = "seed_soft"

    CONFIG = build_scraper_config(
        url=FEMALE_DRIVERS_LIST.base_url,
        section_id=constants.FEMALE_DRIVERS_SECTION_ID,
        expected_headers=constants.FEMALE_DRIVERS_HEADERS,
        schema=FemaleDriversTableParser.build_schema(),
        record_factory=RECORD_FACTORIES.builders("special_driver"),
    )

    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        super().__init__(options=options)
        parser = DriversSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser
