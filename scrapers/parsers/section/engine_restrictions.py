from typing import Any

from scrapers.mixins.apply_for_elements import ApplyForElementsMixin
from scrapers.parsers.section.protocol import SectionParser
from scrapers.parsers.section.sublevels import SubSectionParser
from scrapers.parsers.table.engine_restrictions import EngineRestrictionsTableParser


class EngineSubSectionParser(ApplyForElementsMixin, SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = EngineRestrictionsTableParser()

    def parse_group(
        self,
        elements: list,
        *,
        context=None,
    ) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        for section in parsed.get("sub_sub_sections", []):
            self._table_parser.apply_to_payload(section)
        return parsed

    def _apply_engine_restrictions_table_parser(self, payload: dict[str, Any]) -> None:
        for section in payload.get("sub_sub_sections", []):
            self._apply_for_elements(section.get("elements", []))
            self._apply_engine_restrictions_table_parser(section)


class CurrentRulesSectionParser(SectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = EngineSubSectionParser()
