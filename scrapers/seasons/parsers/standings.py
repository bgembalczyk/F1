from typing import Any

from bs4 import BeautifulSoup

from scrapers.seasons.columns.constructor import ConstructorColumn
from scrapers.seasons.columns.driver import DriverColumn
from scrapers.seasons.parsers.constants import MERGED_ENTRY_BASE_KEYS
from scrapers.seasons.parsers.constants import ROUND_LEVEL_RESULT_ATTRIBUTES
from scrapers.seasons.parsers.table import SeasonTableParser


class SeasonStandingsParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse_drivers(
        self,
        soup: BeautifulSoup,
        season_year: int | None = None,
    ) -> list[dict[str, Any]]:
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

    def parse_constructors(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        records = self._parse_standings_table(
            soup,
            section_ids=[
                "World_Constructors'_Championship_standings",
                "International_Cup_for_F1_Constructors_standings",
            ],
            subject_header="Constructor",
            subject_key="constructor",
            subject_column=ConstructorColumn(),
        )
        return self.merge_duplicate_constructors(records)

    def _parse_standings_table(
        self,
        soup: BeautifulSoup,
        *,
        section_ids: list[str],
        subject_header: str,
        subject_key: str,
        subject_column: Any,
        season_year: int | None = None,
    ) -> list[dict[str, Any]]:
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
        records: list[dict[str, Any]],
        *,
        subject_key: str,
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
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
    def _apply_fastest_lap_sharing(records: list[dict[str, Any]]) -> None:
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

    @staticmethod
    def merge_duplicate_constructors(
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []
        i = 0

        while i < len(records):
            current = records[i]
            entries_to_merge = [current]
            j = i + 1

            while j < len(records):
                next_record = records[j]
                should_merge = (
                    current.get("pos") == next_record.get("pos")
                    and current.get("points") == next_record.get("points")
                    and SeasonStandingsParser._same_constructor(
                        current.get("constructor"),
                        next_record.get("constructor"),
                    )
                )

                if not should_merge:
                    break
                entries_to_merge.append(next_record)
                j += 1

            if len(entries_to_merge) > 1:
                merged.append(
                    SeasonStandingsParser._merge_multiple_entries(entries_to_merge),
                )
            else:
                merged.append(current)

            i = j

        return merged

    @staticmethod
    def _same_constructor(
        constructor1: dict[str, Any] | None,
        constructor2: dict[str, Any] | None,
    ) -> bool:
        if constructor1 is None or constructor2 is None:
            return False

        chassis1 = constructor1.get("chassis_constructor", {})
        chassis2 = constructor2.get("chassis_constructor", {})
        engine1 = constructor1.get("engine_constructor", {})
        engine2 = constructor2.get("engine_constructor", {})

        return chassis1.get("text") == chassis2.get("text") and engine1.get(
            "text",
        ) == engine2.get("text")

    @staticmethod
    def _remove_round_level_attributes(round_data: dict[str, Any]) -> None:
        for key in ROUND_LEVEL_RESULT_ATTRIBUTES:
            round_data.pop(key, None)

    @staticmethod
    def _merge_multiple_entries(entries: list[dict[str, Any]]) -> dict[str, Any]:
        if not entries:
            return {}

        merged = dict(entries[0])
        merged.pop("no", None)

        for entry in entries[1:]:
            for key, value in entry.items():
                if key in MERGED_ENTRY_BASE_KEYS:
                    continue
                merged[key] = SeasonStandingsParser._merge_round_value(
                    merged.get(key),
                    value,
                )

        SeasonStandingsParser._cleanup_round_attributes(merged)
        return merged

    @staticmethod
    def _merge_round_value(existing: Any, incoming: Any) -> Any:
        if incoming is None:
            return existing
        if not (
            isinstance(existing, dict)
            and isinstance(incoming, dict)
            and "results" in incoming
        ):
            if isinstance(incoming, dict) and "results" in incoming:
                cleaned = dict(incoming)
                SeasonStandingsParser._remove_round_level_attributes(cleaned)
                return cleaned
            return incoming

        existing_results = existing.get("results")
        new_results = incoming.get("results")
        existing_list = SeasonStandingsParser._as_results_list(existing_results)
        new_list = SeasonStandingsParser._as_results_list(new_results)
        if existing_list or new_list:
            existing["results"] = existing_list + new_list

        for round_key, round_value in incoming.items():
            if round_key in {"results", *ROUND_LEVEL_RESULT_ATTRIBUTES}:
                continue
            if round_key not in existing:
                existing[round_key] = round_value

        SeasonStandingsParser._remove_round_level_attributes(existing)
        return existing

    @staticmethod
    def _as_results_list(results: Any) -> list[Any]:
        """Normalize results to a list, handling both list and dict formats."""
        if isinstance(results, list):
            return results
        if results is not None:
            return [results]
        return []

    @staticmethod
    def _cleanup_round_attributes(merged: dict[str, Any]) -> None:
        for round_data in merged.values():
            if isinstance(round_data, dict) and "results" in round_data:
                SeasonStandingsParser._remove_round_level_attributes(round_data)
