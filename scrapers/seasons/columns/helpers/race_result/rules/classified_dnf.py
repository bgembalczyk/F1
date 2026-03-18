from typing import Any

from scrapers.seasons.columns.helpers.constants import CLASSIFIED_DNF_BACKGROUNDS
from scrapers.seasons.columns.helpers.constants import CLASSIFIED_DNF_MARK
from scrapers.seasons.columns.helpers.constants import CLASSIFIED_DNF_NOTE
from scrapers.seasons.columns.helpers.constants import CLASSIFIED_DNF_START_YEAR
from scrapers.seasons.columns.helpers.race_result.helpers import append_note
from scrapers.seasons.columns.helpers.race_result.rules.context import ResultRuleContext


class ClassifiedDnfRule:
    def apply(self, result: dict[str, Any], context: ResultRuleContext) -> None:
        if self._is_classified_dnf(result, context):
            append_note(result, CLASSIFIED_DNF_NOTE)

    @staticmethod
    def _is_classified_dnf(result: dict[str, Any], context: ResultRuleContext) -> bool:
        marks = result.get("marks") or []
        position = result.get("position")
        return (
            context.season_year is not None
            and context.season_year >= CLASSIFIED_DNF_START_YEAR
            and CLASSIFIED_DNF_MARK in marks
            and context.background in CLASSIFIED_DNF_BACKGROUNDS
            and isinstance(position, int)
        )
