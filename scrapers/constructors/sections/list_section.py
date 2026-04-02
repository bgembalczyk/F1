from __future__ import annotations

import logging
from dataclasses import replace
from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.sections.serializer import build_section_parse_result
from scrapers.base.sections.table_section_parser import TableSectionParser
from scrapers.base.table.parser import HtmlTableParser
from scrapers.constructors.indianapolis_only_constructors_list import IndianapolisOnlySubSectionParser
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.sections.section import SectionParser as WikiSectionParser

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.sections.interface import SectionParseResult
    from scrapers.base.table.config import ScraperConfig

logger = logging.getLogger(__name__)


class CurrentConstructorsTableParser(WikiTableBaseParser):
    table_type = "current_constructors"

    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool:
        expected = {
            "name",
            "engine",
            "licensed in",
            "based in",
            "seasons",
            "entries",
            "constructors' championships",
            "drivers' championships",
            "race victories",
            "pole positions",
            "fastest laps",
            "podiums",
            "drivers",
            "antecedent teams",
        }
        normalized = {header.strip().lower() for header in headers}
        return expected.issubset(normalized)

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {header: header.strip().lower().replace(" ", "_") for header in headers}


class FormerConstructorsTableParser(WikiTableBaseParser):
    table_type = "former_constructors"

    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool:
        expected = {
            "name",
            "licensed in",
            "seasons",
            "entries",
            "starts",
            "wins",
            "points",
            "pole positions",
            "fastest laps",
            "podiums",
        }
        normalized = {header.strip().lower() for header in headers}
        return expected.issubset(normalized)

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {header: header.strip().lower().replace(" ", "_") for header in headers}


class _ConstructorsTableSectionParser(WikiSectionParser):
    def __init__(
        self,
        *,
        config: ScraperConfig,
        section_label: str | None,
        include_urls: bool,
        normalize_empty_values: bool,
        table_parser: WikiTableBaseParser,
    ) -> None:
        super().__init__()
        self._include_urls = include_urls
        self._parser = TableSectionParser(
            config=config,
            section_id=config.section_id or "constructors",
            section_label=section_label or "Constructors",
            domain="constructors",
            include_urls=include_urls,
            normalize_empty_values=normalize_empty_values,
        )
        self._table_parser = table_parser
        self._html_table_parser = HtmlTableParser()

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        table = section_fragment.find("table", class_="wikitable")
        if table is not None:
            try:
                rows = self._html_table_parser.parse_table(table)
                headers = rows[0].headers if rows else []
                row_maps = [
                    {
                        header: cell.get_text(" ", strip=True)
                        for header, cell in zip(row.headers, row.cells, strict=False)
                    }
                    for row in rows
                ]
                self._table_parser.parse({"headers": headers, "rows": row_maps})
            except RuntimeError:
                pass
        try:
            return self._parser.parse(section_fragment)
        except RuntimeError:
            logger.warning(
                "Skipping constructors section '%s': matching table not found.",
                self._parser._section_label,
            )
            return build_section_parse_result(
                section_id=self._parser._section_id,
                section_label=self._parser._section_label,
                records=[],
                parser=self.__class__.__name__,
                source="wikipedia",
                extras={"domain": "constructors", "skipped": True},
            )


class ConstructorsListSectionParser(_ConstructorsTableSectionParser):
    def __init__(
        self,
        *,
        config: ScraperConfig,
        section_label: str | None = None,
        include_urls: bool,
        normalize_empty_values: bool,
    ) -> None:
        super().__init__(
            config=config,
            section_label=section_label,
            include_urls=include_urls,
            normalize_empty_values=normalize_empty_values,
            table_parser=CurrentConstructorsTableParser(),
        )


class CurrentConstructorsSectionParser(_ConstructorsTableSectionParser):
    def __init__(
        self,
        *,
        config: ScraperConfig,
        section_label: str | None = None,
        include_urls: bool,
        normalize_empty_values: bool,
    ) -> None:
        super().__init__(
            config=config,
            section_label=section_label,
            include_urls=include_urls,
            normalize_empty_values=normalize_empty_values,
            table_parser=CurrentConstructorsTableParser(),
        )


class FormerConstructorsSectionParser(_ConstructorsTableSectionParser):
    def __init__(
        self,
        *,
        config: ScraperConfig,
        section_label: str | None = None,
        include_urls: bool,
        normalize_empty_values: bool,
    ) -> None:
        super().__init__(
            config=config,
            section_label=section_label,
            include_urls=include_urls,
            normalize_empty_values=normalize_empty_values,
            table_parser=FormerConstructorsTableParser(),
        )
        self._indianapolis_sub_section_parser = IndianapolisOnlySubSectionParser()

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        base_result = super().parse(section_fragment)
        indianapolis_records = self._parse_indianapolis_records(section_fragment)
        if not indianapolis_records:
            return base_result
        return replace(base_result, records=[*base_result.records, *indianapolis_records])

    def _parse_indianapolis_records(
        self,
        section_fragment: BeautifulSoup,
    ) -> list[dict[str, Any]]:
        parsed = self._indianapolis_sub_section_parser.parse(section_fragment)
        records = parsed.get("items", [])
        if not isinstance(records, list):
            return []

        if not self._include_urls:
            for record in records:
                if isinstance(record, dict):
                    record.pop("constructor_url", None)
            return records

        for record in records:
            if not isinstance(record, dict):
                continue
            url = record.get("constructor_url")
            if isinstance(url, str) and url.startswith("/"):
                record["constructor_url"] = f"https://en.wikipedia.org{url}"
        return records
