from typing import Any

from scrapers.adapters.factories.dataclass import RECORD_FACTORIES
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.entries_starts import EntriesStartsColumn
from scrapers.columns.types.links_list import LinksListColumn
from scrapers.columns.types.points import PointsColumn
from scrapers.columns.types.seasons import SeasonsColumn
from scrapers.columns.types.skip import SkipColumn
from scrapers.columns.types.url import UrlColumn
from scrapers.config_table import build_scraper_config
from scrapers.constants_drivers import FEMALE_DRIVER_ENTRIES_STARTS_HEADER
from scrapers.constants_drivers import FEMALE_DRIVER_NAME_HEADER
from scrapers.constants_drivers import FEMALE_DRIVER_POINTS_HEADER
from scrapers.constants_drivers import FEMALE_DRIVER_SEASONS_HEADER
from scrapers.constants_drivers import FEMALE_DRIVER_TEAMS_HEADER
from scrapers.constants_drivers import FEMALE_DRIVERS_HEADERS
from scrapers.constants_drivers import FEMALE_DRIVERS_INDEX_HEADER
from scrapers.constants_drivers import FEMALE_DRIVERS_SECTION_ID
from scrapers.mixins.apply_for_elements import ApplyForElementsMixin
from scrapers.options import ScraperOptions
from scrapers.parsers.wiki.nested_wiki import NestedWikiSectionParser
from scrapers.parsers.wiki_table_base_mapper import WikiTableBaseMapper
from scrapers.parsers.wiki.sublevels_nested_section.sub_section import SubSectionParser
from scrapers.scraper_table import F1TableScraper
from scrapers.source_catalog import FEMALE_DRIVERS_LIST
from scrapers.table_schema_dsl import TableSchemaDSL


class FemaleDriversTableMapper(WikiTableBaseMapper):
    table_type = "female_drivers_list"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        FEMALE_DRIVER_NAME_HEADER: "driver",
        FEMALE_DRIVER_SEASONS_HEADER: "seasons",
        FEMALE_DRIVER_TEAMS_HEADER: "teams",
        FEMALE_DRIVER_ENTRIES_STARTS_HEADER: "entries_starts",
        FEMALE_DRIVER_POINTS_HEADER: "points",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = set(FEMALE_DRIVERS_HEADERS)
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
                ColumnSpec(
                    FEMALE_DRIVERS_INDEX_HEADER,
                    "_skip",
                    SkipColumn(),
                ),
                ColumnSpec(
                    FEMALE_DRIVER_NAME_HEADER,
                    "driver",
                    UrlColumn(),
                ),
                ColumnSpec(
                    FEMALE_DRIVER_SEASONS_HEADER,
                    "seasons",
                    SeasonsColumn(),
                ),
                ColumnSpec(
                    FEMALE_DRIVER_TEAMS_HEADER,
                    "teams",
                    LinksListColumn(),
                ),
                ColumnSpec(
                    FEMALE_DRIVER_ENTRIES_STARTS_HEADER,
                    "entries_starts",
                    EntriesStartsColumn(),
                ),
                ColumnSpec(
                    FEMALE_DRIVER_POINTS_HEADER,
                    "points",
                    PointsColumn(),
                ),
            ],
        )


class OfficialDriversSubSectionParser(SubSectionParser, ApplyForElementsMixin):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = FemaleDriversTableMapper()

    def _parse_group(
        self,
        elements: list,
        *,
        context=None,
    ) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self._apply_table_parser_to_sections(parsed, "sub_sub_sections")
        return parsed


class DriversSectionParser(NestedWikiSectionParser):
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
