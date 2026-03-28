from typing import Any

from scrapers.seasons.columns.helpers.constants import F2_INELIGIBLE_YEARS
from scrapers.seasons.columns.helpers.race_result.helpers import append_note
from scrapers.seasons.columns.helpers.race_result.rules.context import ResultRuleContext


class F2EligibilityRule:
    def apply(self, result: dict[str, Any], context: ResultRuleContext) -> None:
        if context.season_year not in F2_INELIGIBLE_YEARS:
            return
        if "1" in context.footnotes:
            result["points_eligible"] = False
            append_note(result, "ineligible_f2")
