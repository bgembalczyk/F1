from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.mappers.seasons_table_mapper import SeasonsTableMapper
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.section.nested_section.base import NestedWikiSectionParser
from scrapers.parsers.wiki.table.html import WikiTableHtmlParser


class SeasonsSectionParser(NestedWikiSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_mapper = SeasonsTableMapper()

    def parse(
        self,
        element: BeautifulSoup,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        parsed = super().parse(element, context=context)
        self._apply_seasons_table_parser(parsed)
        return parsed

    def _parse_group(
        self,
        elements: list,
        *,
        context=None,
    ) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self._apply_seasons_table_parser(parsed)
        return parsed

    def _apply_seasons_table_parser(self, payload: dict[str, Any]) -> None:
        for section in payload.get("sub_sections", []):
            self._apply_for_elements(section.get("elements", []))
            self._apply_seasons_table_parser(section)

    def _apply_for_elements(self, elements: list[dict[str, Any]]) -> None:
        for element in elements:
            if element.get("kind") != "table":
                continue
            data = element.get("data")
            if not isinstance(data, dict):
                continue
            parsed = self._table_mapper.map(data)
            if parsed is not None:
                element["data"] = parsed


class SeasonsTableParser(WikiTableHtmlParser):
    """Concrete parser for seasons list wikitable HTML.

    Parses ``<table class="wikitable">`` elements from the F1 seasons list
    article and returns structured table data.  Domain-level mapping is
    handled separately by :class:`~scrapers.seasons_table_mapper.SeasonsTableMapper`.
    """

    def parse(self, element: Tag) -> dict[str, Any]:  # type: ignore[override]
        return super().parse(element)


__all__ = ["SeasonsSectionParser", "SeasonsTableParser"]
