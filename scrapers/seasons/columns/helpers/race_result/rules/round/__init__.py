"""Backward-compatible package aliases for legacy round-rule imports."""

from scrapers.seasons.columns.helpers.race_result.rules.round_rules import (
    DoublePointsRoundRule,
)
from scrapers.seasons.columns.helpers.race_result.rules.round_rules import (
    HalfPointsRoundRule,
)
from scrapers.seasons.columns.helpers.race_result.rules.round_rules import RoundRule
from scrapers.seasons.columns.helpers.race_result.rules.round_rules import (
    RoundRuleContext,
)

__all__ = [
    "DoublePointsRoundRule",
    "HalfPointsRoundRule",
    "RoundRule",
    "RoundRuleContext",
]
