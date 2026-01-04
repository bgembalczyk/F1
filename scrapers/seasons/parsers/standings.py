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
        return self._merge_duplicate_constructors(records)

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

    @staticmethod
    def _merge_duplicate_constructors(
        records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merge duplicate constructor standings entries that represent the same
        constructor but have separate race results (one per driver).
        
        Only merge entries that:
        - Have the same constructor (chassis + engine)
        - Have the same position
        - Have the same points
        - Don't have a 'no' field (driver number)
        
        When entries have a 'no' field, they represent individual driver results
        and should not be merged.
        """
        merged: List[Dict[str, Any]] = []
        i = 0
        
        while i < len(records):
            current = records[i]
            
            # If this entry has a 'no' field, it's a driver-specific entry - don't merge
            if "no" in current and current["no"] is not None:
                merged.append(current)
                i += 1
                continue
            
            # Look ahead to see if the next entry should be merged with this one
            if i + 1 < len(records):
                next_record = records[i + 1]
                
                # Check if the next record should be merged
                should_merge = (
                    # Next record also has no 'no' field (or it's None)
                    ("no" not in next_record or next_record.get("no") is None)
                    # Same position
                    and current.get("pos") == next_record.get("pos")
                    # Same points
                    and current.get("points") == next_record.get("points")
                    # Same constructor
                    and SeasonStandingsParser._same_constructor(
                        current.get("constructor"), next_record.get("constructor")
                    )
                )
                
                if should_merge:
                    # Merge the two entries
                    merged_entry = SeasonStandingsParser._merge_two_entries(
                        current, next_record
                    )
                    merged.append(merged_entry)
                    i += 2  # Skip both entries
                    continue
            
            # No merge needed, add current entry as-is
            merged.append(current)
            i += 1
        
        return merged

    @staticmethod
    def _same_constructor(
        constructor1: Dict[str, Any] | None, constructor2: Dict[str, Any] | None
    ) -> bool:
        """Check if two constructor objects represent the same constructor."""
        if constructor1 is None or constructor2 is None:
            return False
        
        chassis1 = constructor1.get("chassis_constructor", {})
        chassis2 = constructor2.get("chassis_constructor", {})
        engine1 = constructor1.get("engine_constructor", {})
        engine2 = constructor2.get("engine_constructor", {})
        
        return (
            chassis1.get("text") == chassis2.get("text")
            and engine1.get("text") == engine2.get("text")
        )

    @staticmethod
    def _merge_two_entries(
        entry1: Dict[str, Any], entry2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge two constructor standings entries by combining their race results.
        
        Takes the first entry as the base and merges race results from the second entry.
        """
        merged = dict(entry1)
        
        # Iterate through all keys in the second entry
        for key, value in entry2.items():
            # Skip metadata fields that should come from the first entry
            if key in ("pos", "constructor", "points", "no"):
                continue
            
            # If this is a race result (dict with 'results' key), merge the results
            if isinstance(value, dict) and "results" in value:
                if key in merged and isinstance(merged[key], dict):
                    # Merge the results arrays
                    existing_results = merged[key].get("results", [])
                    new_results = value.get("results", [])
                    # Ensure both are lists before merging
                    if isinstance(existing_results, list) and isinstance(new_results, list):
                        merged[key]["results"] = existing_results + new_results
                else:
                    # This race result doesn't exist in the first entry, add it
                    merged[key] = value
        
        return merged
