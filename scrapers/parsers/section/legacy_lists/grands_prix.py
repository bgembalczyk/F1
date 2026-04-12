from __future__ import annotations

from typing import Any

from scrapers.mixins.apply_for_elements import ApplyForElementsMixin
from scrapers.parsers.section_parser_abc import SubSectionParserABC
from scrapers.parsers.section.nested_section.base import NestedWikiSectionParser
from scrapers.parsers.section.sub_section.base import SubSectionParser
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


class ByRaceTitleSubSectionParser(ApplyForElementsMixin, SubSectionParser):
    def __init__(self, *, table_mapper: WikiTableBaseMapper | None = None, **kwargs: Any) -> None:
        super().__init__(toolbox=kwargs.get("toolbox"))
        self._table_parser = table_mapper or GrandsPrixTableMapper()

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self._apply_table_parser_to_sections(parsed, "sub_sub_sections")
        return parsed


class RacesSectionParser(NestedWikiSectionParser):
    def __init__(self, *, child_parser: SubSectionParserABC | None = None, **kwargs: Any) -> None:
        toolbox = kwargs.get("toolbox")
        super().__init__(toolbox=toolbox)
        self.child_parser = child_parser or ByRaceTitleSubSectionParser(toolbox=toolbox)


__all__ = [
    "ByRaceTitleSubSectionParser",
    "GrandsPrixTableMapper",
    "RacesSectionParser",
]
