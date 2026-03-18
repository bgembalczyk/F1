from typing import Any

from scrapers.seasons.columns.helpers.constants import DOUBLE_POINTS_SEASON_YEAR
from scrapers.seasons.columns.helpers.race_result.rules.round.context import (
    RoundRuleContext,
)


class DoublePointsRoundRule:
    def apply(self, context: RoundRuleContext) -> dict[str, Any] | None:
        if (
            context.season_year == DOUBLE_POINTS_SEASON_YEAR
            and "Abu_Dhabi_Grand_Prix" in context.round_url
            and "‡" in context.marks
        ):
            return {"note": "double_points", "points_multiplier": 2.0}
        return None
