from typing import Any

from scrapers.seasons.columns.race_result import RaceResultColumn


class JimClarkRaceResultColumn(RaceResultColumn):
    """
    Race result column for Jim Clark Trophy.

    In this trophy, * mark at a race result means:
    "competed in insufficient events to be eligible for points"
    """

    def _apply_result_notes(
            self, result: dict[str, Any], background: str | None,
    ) -> None:
        # First apply the standard notes (except for * mark handling)
        super()._apply_result_notes(result, background)

        # Add specific note for Jim Clark Trophy * mark
        marks = result.get("marks") or []
        if "*" in marks and background == "Other classified position":
            # The base class already set points_eligible = False
            # Now add the specific note for Jim Clark Trophy
            self._append_note(result, "insufficient_events_to_be_eligible")
