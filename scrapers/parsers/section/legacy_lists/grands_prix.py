from __future__ import annotations

from typing import Any

from scrapers.parsers.wiki.recursive import RecursiveSectionParser
from scrapers.parsers.wiki.table.base import WikiTableBaseMapper


class GrandsPrixTableMapper(WikiTableBaseMapper):
    table_type = "grands_prix_list"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Race title": "race_title",
        "Country": "country",
        "Years held": "years_held",
        "Circuits": "circuits",
        "Total": "total",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {"Race title", "Years held"}
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }


class ByRaceTitleSubSectionParser(RecursiveSectionParser):
    heading_class = "mw-heading4"
    output_key = "sub_sub_sections"

    def __init__(
        self,
        *,
        table_mapper: WikiTableBaseMapper | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(toolbox=kwargs.get("toolbox"))
        self._table_parser = table_mapper or GrandsPrixTableMapper()

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self._apply_table_parser_to_sections(parsed, "sub_sub_sections")
        return parsed


class RacesSectionParser(RecursiveSectionParser):
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
            child_parser=child_parser or ByRaceTitleSubSectionParser(toolbox=toolbox),
            toolbox=toolbox,
        )


__all__ = [
    "ByRaceTitleSubSectionParser",
    "GrandsPrixTableMapper",
    "RacesSectionParser",
]
