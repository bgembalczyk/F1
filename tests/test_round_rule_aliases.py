"""Tests for backward-compatible round rule alias package.

These tests verify that the round/ package aliases correctly re-export
symbols from round_rules.py and that imports function correctly.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Package-level __init__ aliases
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_round_package_exports_double_points_round_rule() -> None:
    from scrapers.seasons.columns.helpers.race_result.rules.round import (
        DoublePointsRoundRule,
    )

    assert DoublePointsRoundRule is not None
    instance = DoublePointsRoundRule()
    assert hasattr(instance, "apply")


@pytest.mark.unit()
def test_round_package_exports_half_points_round_rule() -> None:
    from scrapers.seasons.columns.helpers.race_result.rules.round import (
        HalfPointsRoundRule,
    )

    assert HalfPointsRoundRule is not None
    instance = HalfPointsRoundRule()
    assert hasattr(instance, "apply")


@pytest.mark.unit()
def test_round_package_exports_round_rule_protocol() -> None:
    from scrapers.seasons.columns.helpers.race_result.rules.round import RoundRule

    assert RoundRule is not None


@pytest.mark.unit()
def test_round_package_exports_round_rule_context() -> None:
    from scrapers.seasons.columns.helpers.race_result.rules.round import RoundRuleContext

    ctx = RoundRuleContext(
        season_year=2014,
        marks=["‡"],
        header_text="Abu Dhabi",
        round_url="Abu_Dhabi_Grand_Prix",
    )
    assert ctx.season_year == 2014


# ---------------------------------------------------------------------------
# Sub-module aliases
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_context_alias_module_exports_round_rule_context() -> None:
    from scrapers.seasons.columns.helpers.race_result.rules.round.context import (
        RoundRuleContext,
    )

    ctx = RoundRuleContext(
        season_year=None,
        marks=[],
        header_text="test",
        round_url="test_url",
    )
    assert ctx.season_year is None


@pytest.mark.unit()
def test_double_points_alias_module_exports_double_points_rule() -> None:
    from scrapers.seasons.columns.helpers.race_result.rules.round.double_points import (
        DoublePointsRoundRule,
    )

    rule = DoublePointsRoundRule()
    assert hasattr(rule, "apply")


@pytest.mark.unit()
def test_half_points_alias_module_exports_half_points_rule() -> None:
    from scrapers.seasons.columns.helpers.race_result.rules.round.half_points import (
        HalfPointsRoundRule,
    )

    rule = HalfPointsRoundRule()
    assert hasattr(rule, "apply")


@pytest.mark.unit()
def test_protocol_alias_module_exports_round_rule() -> None:
    from scrapers.seasons.columns.helpers.race_result.rules.round.protocol import (
        RoundRule,
    )

    assert RoundRule is not None


# ---------------------------------------------------------------------------
# Verify aliases point to the same objects as original round_rules module
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_round_aliases_match_round_rules_originals() -> None:
    from scrapers.seasons.columns.helpers.race_result.rules import round_rules
    from scrapers.seasons.columns.helpers.race_result.rules.round import (
        DoublePointsRoundRule,
        HalfPointsRoundRule,
        RoundRule,
        RoundRuleContext,
    )

    assert DoublePointsRoundRule is round_rules.DoublePointsRoundRule
    assert HalfPointsRoundRule is round_rules.HalfPointsRoundRule
    assert RoundRule is round_rules.RoundRule
    assert RoundRuleContext is round_rules.RoundRuleContext
