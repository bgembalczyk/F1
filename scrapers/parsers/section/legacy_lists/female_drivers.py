from __future__ import annotations

from typing import Any

from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.entries_starts import EntriesStartsColumn
from scrapers.columns.types.links_list import LinksListColumn
from scrapers.columns.types.points import PointsColumn
from scrapers.columns.types.seasons import SeasonsColumn
from scrapers.columns.types.skip import SkipColumn
from scrapers.columns.types.url import UrlColumn
from scrapers.constants_drivers import FEMALE_DRIVER_ENTRIES_STARTS_HEADER
from scrapers.constants_drivers import FEMALE_DRIVER_NAME_HEADER
from scrapers.constants_drivers import FEMALE_DRIVER_POINTS_HEADER
from scrapers.constants_drivers import FEMALE_DRIVER_SEASONS_HEADER
from scrapers.constants_drivers import FEMALE_DRIVER_TEAMS_HEADER
from scrapers.constants_drivers import FEMALE_DRIVERS_HEADERS
from scrapers.constants_drivers import FEMALE_DRIVERS_INDEX_HEADER
from scrapers.mixins.apply_for_elements import ApplyForElementsMixin
from scrapers.parsers.section_parser_abc import SectionParserABC
from scrapers.parsers.section_parser_abc import SubSectionParserABC
from scrapers.parsers.wiki.base_nested_section.nested_section.base import NestedWikiSectionParser
from scrapers.parsers.wiki.base_nested_section.sub_section.base import SubSectionParser
from scrapers.parsers.wiki.table.base import WikiTableBaseMapper
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
                ColumnSpec(FEMALE_DRIVERS_INDEX_HEADER, "_skip", SkipColumn()),
                ColumnSpec(FEMALE_DRIVER_NAME_HEADER, "driver", UrlColumn()),
                ColumnSpec(FEMALE_DRIVER_SEASONS_HEADER, "seasons", SeasonsColumn()),
                ColumnSpec(FEMALE_DRIVER_TEAMS_HEADER, "teams", LinksListColumn()),
                ColumnSpec(FEMALE_DRIVER_ENTRIES_STARTS_HEADER, "entries_starts", EntriesStartsColumn()),
                ColumnSpec(FEMALE_DRIVER_POINTS_HEADER, "points", PointsColumn()),
            ],
        )


class OfficialDriversSubSectionParser(SubSectionParser, ApplyForElementsMixin, SubSectionParserABC):
    def __init__(self, *, table_mapper: WikiTableBaseMapper | None = None, **kwargs: Any) -> None:
        super().__init__(toolbox=kwargs.get("toolbox"))
        self._table_parser = table_mapper or FemaleDriversTableMapper()

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self._apply_table_parser_to_sections(parsed, "sub_sub_sections")
        return parsed


class DriversSectionParser(NestedWikiSectionParser, SectionParserABC):
    def __init__(self, *, child_parser: SubSectionParserABC | None = None, **kwargs: Any) -> None:
        toolbox = kwargs.get("toolbox")
        super().__init__(toolbox=toolbox)
        self.child_parser = child_parser or OfficialDriversSubSectionParser(toolbox=toolbox)


__all__ = [
    "DriversSectionParser",
    "FemaleDriversTableMapper",
    "OfficialDriversSubSectionParser",
]
