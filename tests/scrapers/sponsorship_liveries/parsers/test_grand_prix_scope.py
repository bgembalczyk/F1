# ruff: noqa: E501, PLR2004
"""Tests for GrandPrixScopeTransformer covering uncovered lines."""

from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.grand_prix_scope import (
    GrandPrixScopeTransformer,
)


class TestParamsContainOnlyYearsOrGrandPrix:
    def test_empty_params_returns_true(self):
        assert (
            GrandPrixScopeTransformer.params_contain_only_years_or_grand_prix([])
            is True
        )

    def test_year_param_only(self):
        assert (
            GrandPrixScopeTransformer.params_contain_only_years_or_grand_prix(["1988"])
            is True
        )

    def test_grand_prix_param(self):
        assert (
            GrandPrixScopeTransformer.params_contain_only_years_or_grand_prix(
                ["Monaco Grand Prix"],
            )
            is True
        )

    def test_non_year_non_gp_returns_false(self):
        assert (
            GrandPrixScopeTransformer.params_contain_only_years_or_grand_prix(
                ["some sponsor text"],
            )
            is False
        )

    def test_mixed_year_and_gp(self):
        params = ["1988", "Monaco Grand Prix", "1990"]
        assert (
            GrandPrixScopeTransformer.params_contain_only_years_or_grand_prix(params)
            is True
        )


class TestParseGrandPrixScope:
    def test_empty_params_returns_none(self):
        result = GrandPrixScopeTransformer.parse_grand_prix_scope([])
        assert result is None

    def test_invalid_params_returns_none(self):
        result = GrandPrixScopeTransformer.parse_grand_prix_scope(["some sponsor text"])
        assert result is None

    def test_year_only_params_returns_none(self):
        # Year-only params → accumulator has no entries → returns None
        result = GrandPrixScopeTransformer.parse_grand_prix_scope(["1988"])
        assert result is None

    def test_grand_prix_params_returns_scope(self):
        result = GrandPrixScopeTransformer.parse_grand_prix_scope(["Monaco Grand Prix"])
        assert result is not None
        assert result["type"] == "only"

    def test_invalid_non_gp_text_makes_scope_invalid(self):
        result = GrandPrixScopeTransformer.parse_grand_prix_scope(
            ["Monaco Grand Prix", "not gp text"],
        )
        assert result is None

    def test_onwards_param_builds_range(self):
        result = GrandPrixScopeTransformer.parse_grand_prix_scope(
            ["Monaco Grand Prix onwards"],
        )
        assert result is not None
        assert result["type"] == "range"
        assert result["to"] is None

    def test_range_param_builds_range_scope(self):
        result = GrandPrixScopeTransformer.parse_grand_prix_scope(
            ["Monaco Grand Prix to British Grand Prix"],
        )
        assert result is not None
        assert result["type"] == "range"
        assert "from" in result
        assert "to" in result


class TestConsumesScopeParam:
    def test_year_param_is_skipped(self):
        from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.scope_accumulators.grand_prix_scope import (
            GrandPrixScopeAccumulator,
        )

        acc = GrandPrixScopeAccumulator()
        GrandPrixScopeTransformer._consume_scope_param(acc, "1988")
        assert not acc.entries
        assert not acc.invalid

    def test_non_gp_text_marks_invalid(self):
        from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.scope_accumulators.grand_prix_scope import (
            GrandPrixScopeAccumulator,
        )

        acc = GrandPrixScopeAccumulator()
        GrandPrixScopeTransformer._consume_scope_param(acc, "some other text")
        assert acc.invalid


class TestBuildGrandPrixEntry:
    def test_dict_param_with_url(self):
        entry = GrandPrixScopeTransformer.build_grand_prix_entry(
            {"url": "http://example.com"},
            "Monaco Grand Prix",
        )
        assert entry == {"text": "Monaco Grand Prix", "url": "http://example.com"}

    def test_dict_param_without_url(self):
        entry = GrandPrixScopeTransformer.build_grand_prix_entry(
            {"text": "Monaco Grand Prix"},
            "Monaco Grand Prix",
        )
        assert entry == {"text": "Monaco Grand Prix"}

    def test_string_param(self):
        entry = GrandPrixScopeTransformer.build_grand_prix_entry(
            "Monaco Grand Prix",
            "Monaco Grand Prix",
        )
        assert entry == {"text": "Monaco Grand Prix"}


class TestParseGrandPrixNames:
    def test_simple_grand_prix(self):
        result = GrandPrixScopeTransformer.parse_grand_prix_names("Monaco")
        assert any("Monaco" in name for name in result)

    def test_multiple_with_comma(self):
        result = GrandPrixScopeTransformer.parse_grand_prix_names("Monaco, British")
        assert len(result) >= 2

    def test_grands_prix_replaced(self):
        result = GrandPrixScopeTransformer.parse_grand_prix_names("Grands Prix")
        assert result is not None

    def test_and_separator(self):
        result = GrandPrixScopeTransformer.parse_grand_prix_names("Monaco and British")
        assert len(result) >= 2


class TestGrandPrixScopeKey:
    def test_only_type(self):
        scope = {
            "type": "only",
            "grand_prix": [{"text": "Monaco Grand Prix", "url": "http://example.com"}],
        }
        key = GrandPrixScopeTransformer.grand_prix_scope_key(scope)
        assert key[0] == "only"
        assert ("Monaco Grand Prix", "http://example.com") in key[1]

    def test_only_type_with_plain_string_entry(self):
        scope = {"type": "only", "grand_prix": ["Monaco Grand Prix"]}
        key = GrandPrixScopeTransformer.grand_prix_scope_key(scope)
        assert key[0] == "only"

    def test_range_type(self):
        scope = {
            "type": "range",
            "from": {"text": "Monaco Grand Prix", "url": "http://example.com/monaco"},
            "to": {"text": "British Grand Prix"},
        }
        key = GrandPrixScopeTransformer.grand_prix_scope_key(scope)
        assert key[0] == "range"
        assert key[1] == "Monaco Grand Prix"
        assert key[3] == "British Grand Prix"

    def test_other_type(self):
        scope = {"type": "unknown"}
        key = GrandPrixScopeTransformer.grand_prix_scope_key(scope)
        assert key == ("other",)

    def test_no_type(self):
        key = GrandPrixScopeTransformer.grand_prix_scope_key({})
        assert key == ("other",)

    def test_only_with_empty_entries(self):
        scope = {"type": "only", "grand_prix": None}
        key = GrandPrixScopeTransformer.grand_prix_scope_key(scope)
        assert key[0] == "only"
        assert key[1] == ()
