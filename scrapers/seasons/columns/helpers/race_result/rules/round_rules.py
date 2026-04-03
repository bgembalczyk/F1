from dataclasses import dataclass
from typing import Any, Protocol

from scrapers.seasons.columns.helpers.constants import DOUBLE_POINTS_SEASON_YEAR


@dataclass(frozen=True)
class RoundRuleContext:
    season_year: int | None
    marks: list[str]
    header_text: str
    round_url: str


class RoundRule(Protocol):
    def apply(self, context: RoundRuleContext) -> dict[str, Any] | None: ...


class HalfPointsRoundRule:
    def apply(self, context: RoundRuleContext) -> dict[str, Any] | None:
        if context.header_text == "500" or "Indianapolis_500" in context.round_url:
            return None
        if any(mark in {"*", "†", "‡"} for mark in context.marks):
            return {"note": "half_points", "points_multiplier": 0.5}
        return None


class DoublePointsRoundRule:
    def apply(self, context: RoundRuleContext) -> dict[str, Any] | None:
        if (
            context.season_year == DOUBLE_POINTS_SEASON_YEAR
            and "Abu_Dhabi_Grand_Prix" in context.round_url
            and "‡" in context.marks
        ):
            return {"note": "double_points", "points_multiplier": 2.0}
        return None
