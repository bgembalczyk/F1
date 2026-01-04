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
        # First apply the standard notes
        super()._apply_result_notes(result, background)
        
        # Override the * mark behavior for Colin Chapman Trophy
        marks = result.get("marks") or []
        if "*" in marks:
            # For Colin Chapman Trophy, * means single car entry
            result["points_eligible"] = False
            # Remove the generic "ineligible_for_points" note if it was added
            notes = result.get("notes", [])
            if "ineligible_for_points" in notes:
                notes.remove("ineligible_for_points")
            # Add the specific note for single car entry
            self._append_note(result, "single_car_entry_no_points")
