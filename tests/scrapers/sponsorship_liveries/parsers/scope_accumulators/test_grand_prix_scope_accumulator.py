# ruff: noqa: E501, PLR2004
"""Tests for GrandPrixScopeAccumulator covering lines 13, 15, 18."""

from scrapers.sponsorship_liveries.parsers.scope_accumulators.grand_prix_scope import (
    GrandPrixScopeAccumulator,
)


class TestBuildScope:
    def test_returns_range_scope_when_set(self):
        acc = GrandPrixScopeAccumulator()
        acc.range_scope = {"type": "range", "from": {"text": "Monaco Grand Prix"}, "to": {"text": "British Grand Prix"}}
        result = acc.build_scope()
        assert result == acc.range_scope

    def test_returns_range_from_when_has_onwards_and_entries(self):
        acc = GrandPrixScopeAccumulator()
        acc.has_onwards = True
        acc.entries = [{"text": "Italian Grand Prix"}]
        result = acc.build_scope()
        assert result == {"type": "range", "from": {"text": "Italian Grand Prix"}, "to": None}

    def test_returns_only_when_entries_no_onwards(self):
        acc = GrandPrixScopeAccumulator()
        acc.entries = [{"text": "Monaco Grand Prix"}, {"text": "British Grand Prix"}]
        result = acc.build_scope()
        assert result == {"type": "only", "grand_prix": [{"text": "Monaco Grand Prix"}, {"text": "British Grand Prix"}]}

    def test_returns_none_when_no_entries_no_onwards(self):
        acc = GrandPrixScopeAccumulator()
        result = acc.build_scope()
        assert result is None

    def test_onwards_without_entries_returns_none(self):
        acc = GrandPrixScopeAccumulator()
        acc.has_onwards = True
        result = acc.build_scope()
        assert result is None
