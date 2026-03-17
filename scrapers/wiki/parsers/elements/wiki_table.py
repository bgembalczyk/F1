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
        mapped_rows = [
            self._map_row(row, column_map) for row in table_data.get("rows", [])
        ]

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


class MappedWikiTableParser(WikiTableBaseParser):
    """Parser oparty o statyczną mapę nagłówków i wymagane kolumny."""

    required_header_groups: tuple[frozenset[str], ...] = ()
    column_mapping: dict[str, str] = {}

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        header_set = set(headers)
        return all(bool(header_set & group) for group in self.required_header_groups)

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self.column_mapping[header]
            for header in headers
            if header in self.column_mapping
        }


class StandingsTableParser(MappedWikiTableParser):
    table_type = "standings"
    missing_columns_policy = "fail_if_missing_subject_or_points"
    extra_columns_policy = "collect_as_round_columns"

    required_header_groups = (
        frozenset({"Pos", "Pos."}),
        frozenset({"Points", "Pts", "Pts."}),
        frozenset({"Driver", "Constructor"}),
    )
    column_mapping = {
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


class RaceResultsTableParser(MappedWikiTableParser):
    table_type = "race_results"
    missing_columns_policy = "require_round_and_winner"
    extra_columns_policy = "ignore"

    required_header_groups = (
        frozenset({"Round"}),
        frozenset({"Winning driver"}),
    )
    column_mapping = {
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


class LapRecordsWikiTableParser(MappedWikiTableParser):
    table_type = "lap_records"
    missing_columns_policy = "require_time_and_driver"
    extra_columns_policy = "ignore"

    required_header_groups = (
        frozenset({"Time"}),
        frozenset({"Driver", "Driver/Rider"}),
    )
    column_mapping = {
        "Time": "time",
        "Driver": "driver",
        "Driver/Rider": "driver",
        "Vehicle": "vehicle",
        "Car": "vehicle",
        "Year": "year",
        "Series": "series",
    }
