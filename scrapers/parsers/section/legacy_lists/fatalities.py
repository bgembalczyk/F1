from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.constants.constants_drivers import FATALITIES_AGE_HEADER
from scrapers.constants.constants_drivers import FATALITIES_CAR_HEADER
from scrapers.constants.constants_drivers import FATALITIES_CIRCUIT_HEADER
from scrapers.constants.constants_drivers import FATALITIES_DATE_HEADER
from scrapers.constants.constants_drivers import FATALITIES_DRIVER_HEADER
from scrapers.constants.constants_drivers import FATALITIES_EVENT_HEADER
from scrapers.constants.constants_drivers import FATALITIES_HEADERS
from scrapers.constants.constants_drivers import FATALITIES_REF_HEADER
from scrapers.constants.constants_drivers import FATALITIES_SESSION_HEADER
from scrapers.mappers.driver_ordered_table_mapper import DriverOrderedTableMapper
from scrapers.parsers.wiki.recursive import RecursiveSectionParser
from scrapers.parsers.wiki.table.article_tables_assembler import ArticleTablesAssembler


class FatalitiesTableMapper(DriverOrderedTableMapper):
    table_type = "fatalities_detail_by_driver"
    missing_columns_policy = "require_core_fatalities_columns"
    extra_columns_policy = "ignore"

    _required_headers = frozenset(FATALITIES_HEADERS)
    _column_mapping = {
        FATALITIES_DRIVER_HEADER: "driver",
        FATALITIES_DATE_HEADER: "date",
        FATALITIES_AGE_HEADER: "age",
        FATALITIES_EVENT_HEADER: "event",
        FATALITIES_CIRCUIT_HEADER: "circuit",
        FATALITIES_CAR_HEADER: "car",
        FATALITIES_SESSION_HEADER: "session",
        FATALITIES_REF_HEADER: "ref",
    }

    def matches(self, headers: list[str], _table_data: dict[str, object]) -> bool:
        return self._required_headers.issubset(set(headers))


class DetailByDriverSubSectionParser(RecursiveSectionParser):
    heading_class = "mw-heading4"
    output_key = "sub_sub_sections"

    def __init__(
        self,
        *,
        table_assembler: ArticleTablesAssembler | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(toolbox=kwargs.get("toolbox"))
        self._table_assembler = table_assembler or ArticleTablesAssembler(
            specialized_mappers=[FatalitiesTableMapper()],
        )

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        tags = [element for element in elements if isinstance(element, Tag)]
        section_fragment = BeautifulSoup("", "html.parser")
        for tag in tags:
            section_fragment.append(tag)
        parsed["tables"] = self._table_assembler.assemble(section_fragment)
        return parsed


class FatalitiesSectionParser(RecursiveSectionParser):
    heading_class = "mw-heading3"
    output_key = "sub_sections"

    def __init__(
        self,
        *,
        child_parser: RecursiveSectionParser | None = None,
        **kwargs: Any,
    ) -> None:
        toolbox = kwargs.get("toolbox")
        super().__init__(
            child_parser=child_parser or DetailByDriverSubSectionParser(toolbox=toolbox),
            toolbox=toolbox,
        )


__all__ = [
    "DetailByDriverSubSectionParser",
    "FatalitiesSectionParser",
    "FatalitiesTableMapper",
]
