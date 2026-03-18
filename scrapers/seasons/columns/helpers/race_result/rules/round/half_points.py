from typing import Any

from scrapers.seasons.columns.helpers.race_result.rules.round.context import RoundRuleContext


class HalfPointsRoundRule:
    def apply(self, context: RoundRuleContext) -> dict[str, Any] | None:
        if context.header_text == "500" or "Indianapolis_500" in context.round_url:
            return None
        if any(mark in {"*", "†", "‡"} for mark in context.marks):
            return {"note": "half_points", "points_multiplier": 0.5}
        return None
