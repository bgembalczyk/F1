from __future__ import annotations

from typing import Any

from scrapers.parsers.nested_child import NestedChildParser
from scrapers.parsers.wiki.recursive import RecursiveSectionParser
from scrapers.parsers.wiki.table.base import WikiTableBaseMapper


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


class TyreManufacturersBySeasonSubSectionParser(RecursiveSectionParser):
    heading_class = "mw-heading4"
    output_key = "sub_sub_sections"

    def __init__(
        self,
        *,
        table_mapper: WikiTableBaseMapper | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(toolbox=kwargs.get("toolbox"))
        self._table_mapper = table_mapper or TyreManufacturersBySeasonTableMapper()

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self._table_mapper.apply_to_payload(parsed)
        return parsed


class ManufacturersSectionParser(RecursiveSectionParser):
    heading_class = "mw-heading3"
    output_key = "sub_sections"

    def __init__(
        self,
        *,
        child_parser: NestedChildParser | None = None,
        **kwargs: Any,
    ) -> None:
        toolbox = kwargs.get("toolbox")
        super().__init__(
            child_parser=child_parser
            or TyreManufacturersBySeasonSubSectionParser(toolbox=toolbox),
            toolbox=toolbox,
        )


__all__ = [
    "ManufacturersSectionParser",
    "TyreManufacturersBySeasonSubSectionParser",
    "TyreManufacturersBySeasonTableMapper",
]
