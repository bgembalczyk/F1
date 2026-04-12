from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.parsers.list_element.engine_manufacturers_list import IndianapolisOnlyListParser
from scrapers.parsers.section.sub_section.base import SubSectionParser


class EngineManufacturersIndianapolisSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._list_parser = IndianapolisOnlyListParser()

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self._apply_indianapolis_only_list_parser(parsed)
        return parsed

    def _apply_indianapolis_only_list_parser(self, payload: dict[str, Any]) -> None:
        self._apply_for_elements(payload.get("elements", []))
        for value in payload.values():
            if isinstance(value, dict):
                self._apply_indianapolis_only_list_parser(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._apply_indianapolis_only_list_parser(item)

    def _apply_for_elements(self, elements: list[dict[str, Any]]) -> None:
        for element in elements:
            if element.get("kind") != "list":
                continue
            raw_html = element.get("raw_html_fragment")
            if not isinstance(raw_html, str):
                continue
            parsed_tag = BeautifulSoup(raw_html, "html.parser").find(["ul", "ol"])
            if isinstance(parsed_tag, Tag):
                element["data"] = self._list_parser.parse(parsed_tag)


