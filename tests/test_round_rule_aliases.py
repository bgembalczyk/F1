"""Tests for backward-compatible round rule alias package.

These tests verify that the round/ package aliases correctly re-export
symbols from round_rules.py and that imports function correctly.
"""

from __future__ import annotations

import pytest

from scrapers.seasons.columns_seasons.helpers.race_result.rules import round_rules as rules

ABU_DHABI_DOUBLE_POINTS_YEAR = 2014

# ---------------------------------------------------------------------------
# Package-level __init__ aliases
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_round_package_exports_double_points_round_rule() -> None:
    assert rules.DoublePointsRoundRule is not None
    instance = rules.DoublePointsRoundRule()
    assert hasattr(instance, "apply")


@pytest.mark.unit()
def test_round_package_exports_half_points_round_rule() -> None:
    assert rules.HalfPointsRoundRule is not None
    instance = rules.HalfPointsRoundRule()
    assert hasattr(instance, "apply")


@pytest.mark.unit()
def test_round_package_exports_round_rule_context() -> None:
    ctx = rules.RoundRuleContext(
        season_year=ABU_DHABI_DOUBLE_POINTS_YEAR,
        marks=["‡"],
        header_text="Abu Dhabi",
        round_url="Abu_Dhabi_Grand_Prix",
    )
    assert ctx.season_year == ABU_DHABI_DOUBLE_POINTS_YEAR


# ---------------------------------------------------------------------------
# Sub-module aliases
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_context_alias_module_exports_round_rule_context() -> None:
    ctx = rules.RoundRuleContext(
        season_year=None,
        marks=[],
        header_text="test",
        round_url="test_url",
    )
    assert ctx.season_year is None


@pytest.mark.unit()
def test_double_points_alias_module_exports_double_points_rule() -> None:
    rule = rules.DoublePointsRoundRule()
    assert hasattr(rule, "apply")


@pytest.mark.unit()
def test_half_points_alias_module_exports_half_points_rule() -> None:
    rule = rules.HalfPointsRoundRule()
    assert hasattr(rule, "apply")
