from typing import Any

from scrapers.seasons.columns.race_result import RaceResultColumn


class ColinChapmanRaceResultColumn(RaceResultColumn):
    """
    Race result column for Colin Chapman Trophy.
    
    In this trophy, * mark at a race result means:
    "was not eligible for points, as the team had officially entered only one car for the entire championship"
    """
    
    def _apply_result_notes(
        self, result: dict[str, Any], background: str | None
    ) -> None:
        # First apply the standard notes (except for * mark handling)
        super()._apply_result_notes(result, background)
        
        # Add specific note for Colin Chapman Trophy * mark
        marks = result.get("marks") or []
        if "*" in marks and background == "Other classified position":
            # The base class already set points_eligible = False
            # Now add the specific note for Colin Chapman Trophy
            self._append_note(result, "single_car_entry_no_points")
