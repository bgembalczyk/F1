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
        constructor but have separate race results (one per driver/car number).
        
        Merge entries that:
        - Have the same constructor (chassis + engine)
        - Have the same position
        - Have the same points
        
        The 'no' field (car/driver number) is now used to distinguish which results
        belong to which driver within a merged constructor entry. Each round in the
        merged entry will have multiple results (one per driver).
        """
        merged: List[Dict[str, Any]] = []
        i = 0
        
        while i < len(records):
            current = records[i]
            
            # Collect all consecutive entries that should be merged with current
            entries_to_merge = [current]
            j = i + 1
            
            while j < len(records):
                next_record = records[j]
                
                # Check if the next record should be merged
                should_merge = (
                    # Same position
                    current.get("pos") == next_record.get("pos")
                    # Same points
                    and current.get("points") == next_record.get("points")
                    # Same constructor
                    and SeasonStandingsParser._same_constructor(
                        current.get("constructor"), next_record.get("constructor")
                    )
                )
                
                if should_merge:
                    entries_to_merge.append(next_record)
                    j += 1
                else:
                    break
            
            # Merge all collected entries
            if len(entries_to_merge) > 1:
                merged_entry = SeasonStandingsParser._merge_multiple_entries(
                    entries_to_merge
                )
                merged.append(merged_entry)
            else:
                # No merge needed, add current entry as-is
                merged.append(current)
            
            # Skip all merged entries
            i = j
        
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
    def _remove_round_level_attributes(round_data: dict[str, Any]) -> None:
        """
        Remove attributes that should only exist on individual results.
        Modifies the dictionary in place.
        """
        round_data.pop("background", None)
        round_data.pop("pole_position", None)
        round_data.pop("fastest_lap", None)
    
    @staticmethod
    def _merge_multiple_entries(
        entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merge multiple constructor standings entries by combining their race results.
        
        Takes the first entry as the base and merges race results from all other entries.
        Each result in the results array maintains its own attributes (background, 
        pole_position, fastest_lap, etc.) from its original entry.
        """
        if not entries:
            return {}
        
        merged = dict(entries[0])
        # Remove 'no' field from merged entry as it now represents multiple car/driver numbers
        merged.pop("no", None)
        
        # Iterate through remaining entries
        for entry in entries[1:]:
            for key, value in entry.items():
                # Skip metadata fields that should come from the first entry
                if key in ("pos", "constructor", "points"):
                    continue
                
                # Skip the 'no' field as we want to remove it from merged output
                if key == "no":
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
                        
                        # Remove round-level attributes that should only be on results
                        SeasonStandingsParser._remove_round_level_attributes(merged[key])
                        
                        # Preserve other round attributes (like round info, sprint_position, etc.)
                        for round_key, round_value in value.items():
                            if round_key not in ("results", "background", "pole_position", "fastest_lap"):
                                if round_key not in merged[key]:
                                    merged[key][round_key] = round_value
                    else:
                        # This race result doesn't exist in the first entry, add it
                        # But remove round-level attributes that should only be on results
                        if isinstance(value, dict):
                            value = dict(value)
                            SeasonStandingsParser._remove_round_level_attributes(value)
                        merged[key] = value
        
        # Clean up round-level attributes from existing rounds in the first entry
        # Create a list of items to avoid modifying dictionary during iteration
        for key, value in list(merged.items()):
            if isinstance(value, dict) and "results" in value:
                SeasonStandingsParser._remove_round_level_attributes(value)
        
        return merged
