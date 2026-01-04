from typing import Any

from scrapers.seasons.columns.race_result import RaceResultColumn


class JimClarkRaceResultColumn(RaceResultColumn):
    """
    Race result column for Jim Clark Trophy.
    
    In this trophy, * mark at a race result means:
    "competed in insufficient events to be eligible for points"
    """
    
    def _apply_result_notes(
        self, result: dict[str, Any], background: str | None
    ) -> None:
        # First apply the standard notes
        super()._apply_result_notes(result, background)
        
        # Override the * mark behavior for Jim Clark Trophy
        marks = result.get("marks") or []
        if "*" in marks:
            # For Jim Clark Trophy, * means insufficient events
            result["points_eligible"] = False
            # Remove the generic "ineligible_for_points" note if it was added
            notes = result.get("notes", [])
            if "ineligible_for_points" in notes:
                notes.remove("ineligible_for_points")
            # Add the specific note for insufficient events
            self._append_note(result, "insufficient_events_to_be_eligible")
