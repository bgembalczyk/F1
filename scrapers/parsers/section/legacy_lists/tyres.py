from __future__ import annotations

from typing import Any

from scrapers.parsers.section_parser_abc import SubSectionParserABC
from scrapers.parsers.section.nested_section.base import NestedWikiSectionParser
from scrapers.parsers.section.sub_section.base import SubSectionParser
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


class TyreManufacturersBySeasonSubSectionParser(SubSectionParser):
    def __init__(self, *, table_mapper: WikiTableBaseMapper | None = None, **kwargs: Any) -> None:
        super().__init__(toolbox=kwargs.get("toolbox"))
        self._table_mapper = table_mapper or TyreManufacturersBySeasonTableMapper()

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self._table_mapper.apply_to_payload(parsed)
        return parsed


class ManufacturersSectionParser(NestedWikiSectionParser):
    def __init__(self, *, child_parser: SubSectionParserABC | None = None, **kwargs: Any) -> None:
        toolbox = kwargs.get("toolbox")
        super().__init__(toolbox=toolbox)
        self.child_parser = child_parser or TyreManufacturersBySeasonSubSectionParser(toolbox=toolbox)


__all__ = [
    "ManufacturersSectionParser",
    "TyreManufacturersBySeasonSubSectionParser",
    "TyreManufacturersBySeasonTableMapper",
]
