from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any


class WikiTableBaseParser(ABC):
    """Bazowy parser domenowy dla tabel wikitable.

    Parser operuje na znormalizowanym słowniku tabeli:
    - ``headers``: lista nagłówków
    - ``rows``: lista wierszy jako mapowanie ``header -> value``
    """

    table_type: str = "wiki_table"
    missing_columns_policy: str = "skip"
    extra_columns_policy: str = "ignore"

    def parse(self, table_data: dict[str, Any]) -> dict[str, Any] | None:
        headers = table_data.get("headers", [])
        if not isinstance(headers, list) or not self.matches(headers, table_data):
            return None

        column_map = self.map_columns(headers)
        mapped_rows = [self._map_row(row, column_map) for row in table_data.get("rows", [])]

        return {
            "table_type": self.table_type,
            "domain_column_map": column_map,
            "missing_columns_policy": self.missing_columns_policy,
            "extra_columns_policy": self.extra_columns_policy,
            "domain_rows": mapped_rows,
        }

    @abstractmethod
    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool:
        """Czy parser pasuje do konkretnej tabeli."""

    @abstractmethod
    def map_columns(self, headers: list[str]) -> dict[str, str]:
        """Mapuje nagłówki tabeli na pola domenowe."""

    @staticmethod
    def _map_row(row: dict[str, Any], column_map: dict[str, str]) -> dict[str, Any]:
        mapped: dict[str, Any] = {}
        for header, value in row.items():
            key = column_map.get(header)
            if key:
                mapped[key] = value
        return mapped


class StandingsTableParser(WikiTableBaseParser):
    table_type = "standings"
    missing_columns_policy = "fail_if_missing_subject_or_points"
    extra_columns_policy = "collect_as_round_columns"

    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool:
        header_set = set(headers)
        has_position = bool(header_set & {"Pos", "Pos."})
        has_points = bool(header_set & {"Points", "Pts", "Pts."})
        has_subject = "Driver" in header_set or "Constructor" in header_set
        return has_position and has_points and has_subject

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        mapping = {
            "Pos.": "pos",
            "Pos": "pos",
            "Driver": "driver",
            "Constructor": "constructor",
            "Points": "points",
            "Pts": "points",
            "Pts.": "points",
            "No.": "no",
            "No": "no",
            "Car no.": "no",
        }
        return {header: mapping[header] for header in headers if header in mapping}


class RaceResultsTableParser(WikiTableBaseParser):
    table_type = "race_results"
    missing_columns_policy = "require_round_and_winner"
    extra_columns_policy = "ignore"

    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool:
        header_set = set(headers)
        has_round = "Round" in header_set
        has_winner = "Winning driver" in header_set
        return has_round and has_winner

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        mapping = {
            "Round": "round",
            "Grand Prix": "grand_prix",
            "Race": "grand_prix",
            "Pole position": "pole_position",
            "Pole Position": "pole_position",
            "Fastest lap": "fastest_lap",
            "Winning driver": "winning_driver",
            "Winning constructor": "winning_constructor",
            "Constructor": "winning_constructor",
            "Report": "report",
            "Tyre": "tyre",
        }
        return {header: mapping[header] for header in headers if header in mapping}


class LapRecordsWikiTableParser(WikiTableBaseParser):
    table_type = "lap_records"
    missing_columns_policy = "require_time_and_driver"
    extra_columns_policy = "ignore"

    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool:
        header_set = set(headers)
        has_time = "Time" in header_set
        has_driver = "Driver" in header_set or "Driver/Rider" in header_set
        return has_time and has_driver

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        mapping = {
            "Time": "time",
            "Driver": "driver",
            "Driver/Rider": "driver",
            "Vehicle": "vehicle",
            "Car": "vehicle",
            "Year": "year",
            "Series": "series",
        }
        return {header: mapping[header] for header in headers if header in mapping}
