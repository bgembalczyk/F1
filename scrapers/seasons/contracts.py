from __future__ import annotations

from typing import Any
from typing import Protocol

from bs4 import BeautifulSoup


class SeasonTextSectionExtractionServiceProtocol(Protocol):
    def extract(self, soup: BeautifulSoup) -> dict[str, list[dict[str, Any]]]: ...


class SeasonRecordAssemblerProtocol(Protocol):
    def assemble(
        self,
        *,
        entries: list[dict[str, Any]],
        free_practice_drivers: list[dict[str, Any]],
        calendar: list[dict[str, Any]],
        cancelled_rounds: list[dict[str, Any]],
        testing_venues_and_dates: list[dict[str, Any]],
        results: list[dict[str, Any]],
        non_championship_races: list[dict[str, Any]],
        scoring_system: list[dict[str, Any]],
        drivers_standings: list[dict[str, Any]],
        constructors_standings: list[dict[str, Any]],
        jim_clark_trophy: list[dict[str, Any]],
        colin_chapman_trophy: list[dict[str, Any]],
        south_african_formula_one_championship: list[dict[str, Any]],
        british_formula_one_championship: list[dict[str, Any]],
        regulation_changes: list[dict[str, Any]],
        mid_season_changes: list[dict[str, Any]],
    ) -> dict[str, Any]: ...


class SeasonSectionParserProtocol(Protocol):
    def parse(self, soup: BeautifulSoup) -> Any: ...
