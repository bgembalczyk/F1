from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.seasons.parsers.table import SeasonTableParser


class SeasonStandingsParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse_drivers(
        self, soup: BeautifulSoup, season_year: int | None = None
    ) -> List[Dict[str, Any]]:
        records = self._parse_standings_table(
            soup,
            section_ids=[
                "World_Drivers'_Championship_standings",
                "World_Championship_of_Drivers_standings",
            ],
            subject_header="Driver",
            subject_key="driver",
            subject_column=DriverColumn(),
            season_year=season_year,
        )
        records = self._apply_ineligible_section(records, subject_key="driver")
        self._apply_fastest_lap_sharing(records)
        return records

    def parse_constructors(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._parse_standings_table(
            soup,
            section_ids=[
                "World_Constructors'_Championship_standings",
                "International_Cup_for_F1_Constructors_standings",
            ],
            subject_header="Constructor",
            subject_key="constructor",
            subject_column=ConstructorColumn(),
        )

    def _parse_standings_table(
        self,
        soup: BeautifulSoup,
        *,
        section_ids: list[str],
        subject_header: str,
        subject_key: str,
        subject_column: Any,
        season_year: int | None = None,
    ) -> List[Dict[str, Any]]:
        return self._table_parser.parse_standings_table(
            soup,
            section_ids=section_ids,
            subject_header=subject_header,
            subject_key=subject_key,
            subject_column=subject_column,
            season_year=season_year,
        )

    @staticmethod
    def _apply_ineligible_section(
        records: List[Dict[str, Any]],
        *,
        subject_key: str,
    ) -> List[Dict[str, Any]]:
        filtered: List[Dict[str, Any]] = []
        ineligible = False
        for record in records:
            subject = record.get(subject_key)
            subject_text = None
            if isinstance(subject, dict):
                subject_text = subject.get("text") or ""
            elif isinstance(subject, str):
                subject_text = subject
            if subject_text and "ineligible for Formula One points" in subject_text:
                ineligible = True
                continue
            if ineligible:
                record["eligible_for_points"] = False
            filtered.append(record)
        return filtered

    @staticmethod
    def _apply_fastest_lap_sharing(records: List[Dict[str, Any]]) -> None:
        fastest_lap_counts: dict[str, int] = {}
        for record in records:
            for key, value in record.items():
                if isinstance(value, dict) and value.get("fastest_lap"):
                    fastest_lap_counts[key] = fastest_lap_counts.get(key, 0) + 1

        for record in records:
            for key, value in record.items():
                if not isinstance(value, dict):
                    continue
                if not value.get("fastest_lap"):
                    continue
                count = fastest_lap_counts.get(key, 0)
                if count > 1:
                    value["fastest_lap_shared"] = True
                    value["fastest_lap_share_count"] = count
