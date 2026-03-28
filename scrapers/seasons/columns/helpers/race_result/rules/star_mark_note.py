from typing import Any

from scrapers.seasons.columns.helpers.race_result.helpers import append_note
from scrapers.seasons.columns.helpers.race_result.rules.context import ResultRuleContext


class StarMarkNoteRule:
    def __init__(self, note: str) -> None:
        self._note = note

    def apply(self, result: dict[str, Any], context: ResultRuleContext) -> None:
        marks = result.get("marks") or []
        if "*" in marks and context.background == "Other classified position":
            append_note(result, self._note)
