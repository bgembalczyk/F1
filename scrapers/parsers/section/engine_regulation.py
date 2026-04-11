from typing import Any

from scrapers.parsers.section.base import BaseSectionParser
from scrapers.parsers.section.sublevels import SubSectionParser
from scrapers.parsers.table.engine_regulation import EngineRegulationTableParser


class EngineRegulationSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = EngineRegulationTableParser()

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self._apply_engine_regulation_table_parser(parsed)
        return parsed

    def _apply_engine_regulation_table_parser(self, payload: dict[str, Any]) -> None:
        for section in payload.get("sub_sub_sections", []):
            self._apply_for_elements(section.get("elements", []))
            self._apply_engine_regulation_table_parser(section)

    def _apply_for_elements(self, elements: list[dict[str, Any]]) -> None:
        for element in elements:
            if element.get("kind") != "table":
                continue
            data = element.get("data")
            if not isinstance(data, dict):
                continue
            parsed = self._table_parser.parse(data)
            if parsed is not None:
                element["data"] = parsed


class HistorySectionParser(BaseSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = EngineRegulationSubSectionParser()
