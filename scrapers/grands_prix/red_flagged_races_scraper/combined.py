from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.base.table.config import build_scraper_config
from scrapers.grands_prix.red_flagged_races_scraper.base import RedFlaggedRacesBaseScraper
from scrapers.grands_prix.red_flagged_races_scraper.non_championship import (
    RedFlaggedNonChampionshipRacesScraper,
)
from scrapers.grands_prix.red_flagged_races_scraper.world_championship import (
    RedFlaggedWorldChampionshipRacesScraper,
)
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser


class WorldChampionshipsRacesTableParser(WikiTableBaseParser):
    table_type = "red_flagged_world_championship_races"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Year": "season",
        "Grand Prix": "grand_prix",
        "Lap": "lap",
        "R": "restart_status",
        "Winner": "winner",
        "Incident that prompted red flag": "incident",
        "Failed to make the restart - Drivers": "failed_to_make_restart_drivers",
        "Failed to make the restart - Reason": "failed_to_make_restart_reason",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {
            "Year",
            "Grand Prix",
            "Lap",
            "R",
            "Winner",
            "Incident that prompted red flag",
        }
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }


class NonChampionshipsRacesTableParser(WikiTableBaseParser):
    table_type = "red_flagged_non_championship_races"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Year": "season",
        "Event": "event",
        "Lap": "lap",
        "R": "restart_status",
        "Winner": "winner",
        "Incident that prompted red flag": "incident",
        "Failed to make the restart - Drivers": "failed_to_make_restart_drivers",
        "Failed to make the restart - Reason": "failed_to_make_restart_reason",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {
            "Year",
            "Event",
            "Lap",
            "R",
            "Winner",
            "Incident that prompted red flag",
        }
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }


class NonChampionshipsRacesSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = NonChampionshipsRacesTableParser()

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        self._apply_non_championship_table_parser(parsed)
        return parsed

    def _apply_non_championship_table_parser(self, payload: dict[str, Any]) -> None:
        for section in payload.get("sub_sub_sections", []):
            self._apply_for_elements(section.get("elements", []))
            self._apply_non_championship_table_parser(section)

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


class RedFlaggedRacesSectionParser(SectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = NonChampionshipsRacesSubSectionParser()
        self._world_championship_table_parser = WorldChampionshipsRacesTableParser()

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        self._apply_world_championship_table_parser(parsed)
        return parsed

    def _apply_world_championship_table_parser(self, payload: dict[str, Any]) -> None:
        for section in payload.get("sub_sections", []):
            self._apply_for_elements(section.get("elements", []))
            self._apply_world_championship_table_parser(section)

    def _apply_for_elements(self, elements: list[dict[str, Any]]) -> None:
        for element in elements:
            if element.get("kind") != "table":
                continue
            data = element.get("data")
            if not isinstance(data, dict):
                continue
            parsed = self._world_championship_table_parser.parse(data)
            if parsed is not None:
                element["data"] = parsed


class RedFlaggedRacesScraper(RedFlaggedRacesBaseScraper):
    """Composite scraper that returns both world and non-championship red-flagged races."""

    _SUPPORTED_EXPORT_SCOPES = {"all", "world_championship", "non_championship"}

    CONFIG = build_scraper_config(
        url=RedFlaggedWorldChampionshipRacesScraper.CONFIG.url,
        section_id=RedFlaggedWorldChampionshipRacesScraper.CONFIG.section_id,
        expected_headers=RedFlaggedWorldChampionshipRacesScraper.CONFIG.expected_headers,
        schema=RedFlaggedWorldChampionshipRacesScraper.CONFIG.schema,
        record_factory=RedFlaggedWorldChampionshipRacesScraper.CONFIG.record_factory,
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        export_scope: str = "all",
    ) -> None:
        super().__init__(options=options)
        if export_scope not in self._SUPPORTED_EXPORT_SCOPES:
            msg = f"Unsupported export_scope='{export_scope}' for {self.__class__.__name__}"
            raise ValueError(msg)
        self._export_scope = export_scope
        parser = RedFlaggedRacesSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser
        self._world_scraper = RedFlaggedWorldChampionshipRacesScraper(options=options)
        self._non_championship_scraper = RedFlaggedNonChampionshipRacesScraper(
            options=options,
        )

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        if self._export_scope == "world_championship":
            return self._world_scraper.parse_soup(soup)
        if self._export_scope == "non_championship":
            return self._non_championship_scraper.parse_soup(soup)
        world_records = self._world_scraper.parse_soup(soup)
        non_championship_records = self._non_championship_scraper.parse_soup(soup)
        return [*world_records, *non_championship_records]
