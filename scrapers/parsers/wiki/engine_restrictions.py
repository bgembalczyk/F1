from typing import Any

from scrapers.mixins.apply_for_elements import ApplyForElementsMixin
from scrapers.parsers.wiki.base_nested import BaseNestedSectionParser
from scrapers.parsers.wiki.engine_restrictions_wiki_table import EngineRestrictionsTableMapper
from scrapers.parsers.wiki.sublevels.sub_section import SubSectionParser


class EngineSubSectionParser(ApplyForElementsMixin, SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_mapper = EngineRestrictionsTableMapper()

    def _parse_group(
        self,
        elements: list,
        *,
        context=None,
    ) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        for section in parsed.get("sub_sub_sections", []):
            self._table_mapper.apply_to_payload(section)
        return parsed

    def _apply_engine_restrictions_table_parser(self, payload: dict[str, Any]) -> None:
        for section in payload.get("sub_sub_sections", []):
            self._apply_for_elements(section.get("elements", []))
            self._apply_engine_restrictions_table_parser(section)


class CurrentRulesSectionParser(BaseNestedSectionParser):
    heading_class = "mw-heading3"
    output_key = "sub_sections"

    def __init__(self) -> None:
        self.child_parser = EngineSubSectionParser()
        super().__init__(child_parser=self.child_parser)
