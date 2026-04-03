"""Backward-compatible package aliases for legacy round-rule imports."""

from scrapers.seasons.columns.helpers.race_result.rules.round_rules import (
    DoublePointsRoundRule,
    HalfPointsRoundRule,
    RoundRule,
    RoundRuleContext,
)

__all__ = [
    "DoublePointsRoundRule",
    "HalfPointsRoundRule",
    "RoundRule",
    "RoundRuleContext",
]
