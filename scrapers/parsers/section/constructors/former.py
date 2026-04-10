from typing import Any

from bs4 import BeautifulSoup

from scrapers.config_table import TableScraperConfig
from scrapers.parsers.section.constructors.base import ConstructorsSectionParser
from scrapers.parsers.section.sub.indianapolis_only import IndianapolisOnlySubSectionParser
from scrapers.parsers.table.former_constructors import FormerConstructorsTableParser
from scrapers.section.parse_results import SectionParseResult


class FormerConstructorsSectionParser(ConstructorsSectionParser):
    def __init__(
        self,
        *,
        config: TableScraperConfig,
        section_label: str | None = None,
        include_urls: bool,
        normalize_empty_values: bool,
    ) -> None:
        super().__init__(
            config=config,
            section_label=section_label,
            include_urls=include_urls,
            normalize_empty_values=normalize_empty_values,
            table_mapping_parser=FormerConstructorsTableParser(),
        )
        self._indianapolis_sub_section_parser = IndianapolisOnlySubSectionParser()

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        result = super().parse(section_fragment)
        for record in result.records:
            if not isinstance(record, dict) or "constructor" not in record:
                continue
            record["chassis_constructor"] = record.pop("constructor")
        return result

    def parse_indianapolis_only_records(
        self,
        section_fragment: BeautifulSoup,
    ) -> list[dict[str, Any]]:
        parsed = self._indianapolis_sub_section_parser.parse(section_fragment)
        records = parsed.get("items", [])
        if not isinstance(records, list):
            return []

        normalized_records: list[dict[str, Any]] = []
        for record in records:
            if not isinstance(record, dict):
                continue
            normalized_constructor = self._normalize_indianapolis_constructor(record)
            if normalized_constructor is None:
                continue
            if not self._include_urls:
                normalized_constructor.pop("url", None)
            else:
                url = normalized_constructor.get("url")
                if isinstance(url, str) and url.startswith("/"):
                    normalized_constructor["url"] = f"https://en.wikipedia.org{url}"
            normalized_records.append(
                {"chassis_constructor": normalized_constructor},
            )
        return normalized_records

    @staticmethod
    def _normalize_indianapolis_constructor(
        record: dict[str, Any],
    ) -> dict[str, Any] | None:
        constructor = record.get("chassis_constructor")
        if isinstance(constructor, dict):
            return dict(constructor)

        constructor_name = record.get("constructor")
        if not isinstance(constructor_name, str) or not constructor_name.strip():
            return None

        normalized: dict[str, Any] = {"text": constructor_name.strip()}
        constructor_url = record.get("constructor_url")
        if isinstance(constructor_url, str) and constructor_url.strip():
            normalized["url"] = constructor_url.strip()
        return normalized
