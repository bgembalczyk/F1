from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from typing import Any

from bs4 import BeautifulSoup
from models.value_objects import EntityName
from models.value_objects import SectionId

from scrapers.base.sections.serializer import build_section_parse_result
from scrapers.base.sections.table_section_parser import TableSectionParser
from scrapers.base.table.parser import HtmlTableParser
from scrapers.constructors.constants import CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_BASED_IN_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_DRIVERS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_ENGINE_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_FASTEST_LAPS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_LICENSED_IN_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_NAME_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_PODIUMS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_POINTS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_POLES_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_RACES_ENTERED_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_RACES_STARTED_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_SEASONS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_TOTAL_ENTRIES_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_WCC_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_WDC_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_WINS_HEADER
from scrapers.constructors.indianapolis_only_constructors_list import (
    IndianapolisOnlySubSectionParser,
)
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.sections.section import SectionParser as WikiSectionParser

if TYPE_CHECKING:
    from scrapers.base.sections.interface import SectionParseResult
    from scrapers.base.table.config import ScraperConfig

logger = logging.getLogger(__name__)


class CurrentConstructorsTableParser(WikiTableBaseParser):
    table_type = "current_constructors"

    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool:
        del table_data
        expected = {
            CONSTRUCTOR_NAME_HEADER.lower(),
            CONSTRUCTOR_ENGINE_HEADER.lower(),
            CONSTRUCTOR_LICENSED_IN_HEADER.lower(),
            CONSTRUCTOR_BASED_IN_HEADER.lower(),
            CONSTRUCTOR_SEASONS_HEADER.lower(),
            CONSTRUCTOR_RACES_ENTERED_HEADER.lower(),
            CONSTRUCTOR_RACES_STARTED_HEADER.lower(),
            CONSTRUCTOR_TOTAL_ENTRIES_HEADER.lower(),
            CONSTRUCTOR_WINS_HEADER.lower(),
            CONSTRUCTOR_POINTS_HEADER.lower(),
            CONSTRUCTOR_POLES_HEADER.lower(),
            CONSTRUCTOR_FASTEST_LAPS_HEADER.lower(),
            CONSTRUCTOR_PODIUMS_HEADER.lower(),
            CONSTRUCTOR_WCC_HEADER.lower(),
            CONSTRUCTOR_WDC_HEADER.lower(),
            CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER.lower(),
        }
        normalized = {header.strip().lower() for header in headers}
        return expected.issubset(normalized)

    _HEADER_TO_KEY: dict[str, str] = {
        CONSTRUCTOR_NAME_HEADER: "constructor",
        CONSTRUCTOR_ENGINE_HEADER: "engine",
        CONSTRUCTOR_LICENSED_IN_HEADER: "licensed_in",
        CONSTRUCTOR_BASED_IN_HEADER: "based_in",
        CONSTRUCTOR_SEASONS_HEADER: "seasons",
        CONSTRUCTOR_RACES_ENTERED_HEADER: "races_entered",
        CONSTRUCTOR_RACES_STARTED_HEADER: "races_started",
        CONSTRUCTOR_DRIVERS_HEADER: "drivers",
        CONSTRUCTOR_TOTAL_ENTRIES_HEADER: "total_entries",
        CONSTRUCTOR_WINS_HEADER: "wins",
        CONSTRUCTOR_POINTS_HEADER: "points",
        CONSTRUCTOR_POLES_HEADER: "poles",
        CONSTRUCTOR_FASTEST_LAPS_HEADER: "fastest_laps",
        CONSTRUCTOR_PODIUMS_HEADER: "podiums",
        CONSTRUCTOR_WCC_HEADER: "wcc_titles",
        CONSTRUCTOR_WDC_HEADER: "wdc_titles",
        CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER: "antecedent_teams",
    }

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._HEADER_TO_KEY.get(
                header.strip(),
                header.strip().lower().replace(" ", "_"),
            )
            for header in headers
        }


class FormerConstructorsTableParser(WikiTableBaseParser):
    table_type = "former_constructors"

    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool:
        del table_data
        expected = {
            CONSTRUCTOR_NAME_HEADER.lower(),
            CONSTRUCTOR_LICENSED_IN_HEADER.lower(),
            CONSTRUCTOR_SEASONS_HEADER.lower(),
        }
        normalized = {header.strip().lower() for header in headers}
        return expected.issubset(normalized)

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {header: header.strip().lower().replace(" ", "_") for header in headers}


class ConstructorsSectionParser(WikiSectionParser):
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
        logger.warning(
            "Constructors section parser '%s': start parse.",
            self._parser.section_label,
        )
        table = section_fragment.find("table", class_="wikitable")
        logger.warning(
            "Constructors section parser '%s': first wikitable found=%s.",
            self._parser.section_label,
            table is not None,
        )
        if table is not None:
            try:
                rows = self._html_table_parser.parse_table(table)
                headers = rows[0].headers if rows else []
                logger.warning(
                    "Constructors section parser '%s': first table headers=%s.",
                    self._parser.section_label,
                    headers,
                )
                row_maps = [
                    {
                        header: cell.get_text(" ", strip=True)
                        for header, cell in zip(row.headers, row.cells, strict=False)
                    }
                    for row in rows
                ]
                self._table_parser.parse({"headers": headers, "rows": row_maps})
            except RuntimeError:
                logger.warning(
                    "Constructors section parser '%s': "
                    "lightweight table pre-parse failed.",
                    self._parser.section_label,
                )
        try:
            return self._parser.parse(section_fragment)
        except RuntimeError:
            logger.warning(
                "Constructors section parser '%s': full section parse failed, "
                "trying table-only fallback.",
                self._parser.section_label,
            )
            if table is not None:
                table_only_fragment = BeautifulSoup(str(table), "html.parser")
                try:
                    return self._parser.parse(table_only_fragment)
                except RuntimeError:
                    logger.warning(
                        "Constructors section parser '%s': table-only fallback failed.",
                        self._parser.section_label,
                    )
            logger.warning(
                "Skipping constructors section '%s': matching table not found.",
                self._parser.section_label,
            )
            return build_section_parse_result(
                section_id=self._parser.section_id,
                section_label=self._parser.section_label,
                records=[],
                parser=self.__class__.__name__,
                source="wikipedia",
                extras={"domain": "constructors", "skipped": True},
            )


class CurrentConstructorsSectionParser(ConstructorsSectionParser):
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

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        parsed = super().parse(section_fragment)
        sorted_records = [
            self._sort_current_constructor_record_keys(record) for record in parsed.records
        ]
        return build_section_parse_result(
            section_id=str(SectionId.from_raw(parsed.section_id)),
            section_label=EntityName.from_raw(parsed.section_label).to_export(),
            records=sorted_records,
            parser=str(parsed.metadata.get("parser", self.__class__.__name__)),
            source=str(parsed.metadata.get("source", "wikipedia")),
            extras={
                key: value
                for key, value in parsed.metadata.items()
                if key not in {"parser", "source", "heading_path"}
            },
            heading_path=tuple(parsed.metadata.get("heading_path", [])),
        )

    @staticmethod
    def _sort_current_constructor_record_keys(record: dict[str, Any]) -> dict[str, Any]:
        pinned_keys = ("constructor", "engine")
        ordered: dict[str, Any] = {}

        for key in pinned_keys:
            if key in record:
                ordered[key] = record[key]

        remaining_keys = sorted(key for key in record if key not in pinned_keys)
        for key in remaining_keys:
            ordered[key] = record[key]

        return ordered


class FormerConstructorsSectionParser(ConstructorsSectionParser):
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
            normalized = dict(record)
            if not self._include_urls:
                normalized.pop("constructor_url", None)
            else:
                url = normalized.get("constructor_url")
                if isinstance(url, str) and url.startswith("/"):
                    normalized["constructor_url"] = f"https://en.wikipedia.org{url}"
            normalized_records.append(normalized)
        return normalized_records
