"""Tests for low-coverage race result helper and column modules."""

from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.adapters.row_background import HtmlRowBackgroundColorAdapter
from scrapers.seasons.columns.helpers.race_result.background_mapper import (
    RaceResultBackgroundMapper,
)
from scrapers.seasons.columns.helpers.race_result.helpers import append_note
from scrapers.seasons.columns.helpers.race_result.rules.context import ResultRuleContext
from scrapers.seasons.columns.helpers.race_result.rules.fatal_accident import (
    FatalAccidentRule,
)
from scrapers.seasons.columns.helpers.race_result.rules.mark_based_eligibility import (
    MarkBasedEligibilityRule,
)
from scrapers.seasons.helpers import season_filename

# ---------------------------------------------------------------------------
# seasons/helpers.py - season_filename
# ---------------------------------------------------------------------------


def test_season_filename_plain_year() -> None:
    assert season_filename({"text": "1950"}) == "1950.json"


def test_season_filename_slug_for_non_digit_text() -> None:
    assert (
        season_filename({"text": "1950 World Championship"})
        == "1950_world_championship.json"
    )


def test_season_filename_unknown_for_missing_text() -> None:
    assert season_filename({}) == "unknown.json"


def test_season_filename_unknown_for_none_text() -> None:
    assert season_filename({"text": None}) == "unknown.json"


def test_season_filename_strips_whitespace() -> None:
    assert season_filename({"text": "  2023  "}) == "2023.json"


# ---------------------------------------------------------------------------
# seasons/columns/helpers/race_result/helpers.py - append_note
# ---------------------------------------------------------------------------


def test_append_note_adds_note_to_result() -> None:
    result: dict = {}
    append_note(result, "some_note")
    assert result["notes"] == ["some_note"]


def test_append_note_does_not_duplicate_note() -> None:
    result: dict = {"notes": ["some_note"]}
    append_note(result, "some_note")
    assert result["notes"] == ["some_note"]


def test_append_note_appends_distinct_notes() -> None:
    result: dict = {"notes": ["note_a"]}
    append_note(result, "note_b")
    assert result["notes"] == ["note_a", "note_b"]


# ---------------------------------------------------------------------------
# seasons/columns/helpers/race_result/background_mapper.py
# ---------------------------------------------------------------------------


def test_background_mapper_maps_known_color() -> None:
    mapper = RaceResultBackgroundMapper({"ffffbf": "Winner"})
    assert mapper.map("#ffffbf") == "Winner"


def test_background_mapper_returns_none_for_unknown_color() -> None:
    mapper = RaceResultBackgroundMapper({"ffffbf": "Winner"})
    assert mapper.map("#000001") is None


def test_background_mapper_handles_none_background() -> None:
    mapper = RaceResultBackgroundMapper({"ffffbf": "Winner"})
    assert mapper.map(None) is None


def test_background_mapper_expands_short_hex() -> None:
    mapper = RaceResultBackgroundMapper({"aabbcc": "Some Result"})
    assert mapper.map("#abc") == "Some Result"


def test_background_mapper_handles_uppercase_hex() -> None:
    mapper = RaceResultBackgroundMapper({"ffffbf": "Winner"})
    assert mapper.map("#FFFFBF") == "Winner"


def test_background_mapper_returns_none_for_invalid_hex() -> None:
    mapper = RaceResultBackgroundMapper({"ffffbf": "Winner"})
    assert mapper.map("not-a-color") is None


# ---------------------------------------------------------------------------
# seasons/columns/helpers/race_result/rules/mark_based_eligibility.py
# ---------------------------------------------------------------------------


def _make_context(
    *,
    background: str | None = None,
    year: int = 2000,
) -> ResultRuleContext:
    return ResultRuleContext(season_year=year, background=background, footnotes=[])


def test_mark_based_eligibility_star_mark_with_other_classified_sets_ineligible() -> (
    None
):
    rule = MarkBasedEligibilityRule()
    result = {"marks": ["*"], "position": 7}
    rule.apply(result, _make_context(background="Other classified position"))
    assert result["points_eligible"] is False


def test_mark_based_eligibility_star_mark_different_background_no_change() -> None:
    rule = MarkBasedEligibilityRule()
    result = {"marks": ["*"], "position": 7}
    rule.apply(result, _make_context(background="Winner"))
    assert "points_eligible" not in result


def test_mark_based_eligibility_tilde_mark_sets_ineligible_and_adds_note() -> None:
    rule = MarkBasedEligibilityRule()
    result = {"marks": ["~"], "position": 3}
    rule.apply(result, _make_context())
    assert result["points_eligible"] is False
    assert "shared_drive_no_points" in result.get("notes", [])


def test_mark_based_eligibility_double_dagger_with_int_position_sets_ineligible() -> (
    None
):
    rule = MarkBasedEligibilityRule()
    result = {"marks": ["‡"], "position": 5}
    rule.apply(result, _make_context())
    assert result["points_eligible"] is False
    assert "no_points_awarded" in result.get("notes", [])


def test_mark_based_eligibility_double_dagger_non_int_position_no_change() -> None:
    rule = MarkBasedEligibilityRule()
    result = {"marks": ["‡"], "position": "DSQ"}
    rule.apply(result, _make_context())
    assert "points_eligible" not in result


def test_mark_based_eligibility_no_relevant_marks_no_change() -> None:
    rule = MarkBasedEligibilityRule()
    result = {"marks": [], "position": 1}
    rule.apply(result, _make_context())
    assert "points_eligible" not in result


# ---------------------------------------------------------------------------
# seasons/columns/helpers/race_result/rules/fatal_accident.py
# ---------------------------------------------------------------------------


def test_fatal_accident_rule_dns_with_dagger_adds_before_race_note() -> None:
    rule = FatalAccidentRule()
    result = {"marks": ["†"], "position": "DNS"}
    ctx = ResultRuleContext(season_year=1970, background=None, footnotes=[])
    rule.apply(result, ctx)
    assert "fatal_accident_before_race" in result.get("notes", [])


def test_fatal_accident_rule_ret_with_dagger_adds_during_race_note() -> None:
    rule = FatalAccidentRule()
    result = {"marks": ["†"], "position": "Ret"}
    ctx = ResultRuleContext(season_year=1970, background=None, footnotes=[])
    rule.apply(result, ctx)
    assert "fatal_accident_during_race" in result.get("notes", [])


def test_fatal_accident_rule_ret_with_double_dagger_adds_during_race_note() -> None:
    rule = FatalAccidentRule()
    result = {"marks": ["‡"], "position": "Ret"}
    ctx = ResultRuleContext(season_year=1970, background=None, footnotes=[])
    rule.apply(result, ctx)
    assert "fatal_accident_during_race" in result.get("notes", [])


def test_fatal_accident_rule_before_start_year_no_note() -> None:
    rule = FatalAccidentRule()
    result = {"marks": ["†"], "position": "DNS"}
    ctx = ResultRuleContext(season_year=1960, background=None, footnotes=[])
    rule.apply(result, ctx)
    assert "notes" not in result


def test_fatal_accident_rule_integer_position_no_note() -> None:
    rule = FatalAccidentRule()
    result = {"marks": ["†"], "position": 1}
    ctx = ResultRuleContext(season_year=1970, background=None, footnotes=[])
    rule.apply(result, ctx)
    assert "notes" not in result


def test_fatal_accident_rule_none_season_year_no_note() -> None:
    rule = FatalAccidentRule()
    result = {"marks": ["†"], "position": "DNS"}
    ctx = ResultRuleContext(season_year=None, background=None, footnotes=[])
    rule.apply(result, ctx)
    assert "notes" not in result


# ---------------------------------------------------------------------------
# base/adapters/row_background.py - HtmlRowBackgroundColorAdapter
# ---------------------------------------------------------------------------


def _make_tag(html: str):
    return BeautifulSoup(html, "html.parser").find("tr")


def test_row_background_extracts_from_style_attribute() -> None:
    tag = _make_tag('<tr style="background:#ffffbf"><td>test</td></tr>')
    adapter = HtmlRowBackgroundColorAdapter()
    assert adapter.extract(tag) == "ffffbf"


def test_row_background_extracts_from_bgcolor_attribute() -> None:
    tag = _make_tag('<tr bgcolor="#dfdfdf"><td>test</td></tr>')
    adapter = HtmlRowBackgroundColorAdapter()
    assert adapter.extract(tag) == "dfdfdf"


def test_row_background_extracts_from_cell_style() -> None:
    tag = _make_tag('<tr><td style="background:#ffdf9f">test</td></tr>')
    adapter = HtmlRowBackgroundColorAdapter()
    assert adapter.extract(tag) == "ffdf9f"


def test_row_background_returns_none_when_no_color() -> None:
    tag = _make_tag("<tr><td>no color</td></tr>")
    adapter = HtmlRowBackgroundColorAdapter()
    assert adapter.extract(tag) is None


def test_row_background_expands_short_hex() -> None:
    tag = _make_tag('<tr style="background:#abc"><td>test</td></tr>')
    adapter = HtmlRowBackgroundColorAdapter()
    assert adapter.extract(tag) == "aabbcc"


def test_row_background_prefers_row_style_over_cell() -> None:
    tag = _make_tag(
        '<tr style="background:#ffffbf"><td style="background:#dfdfdf">test</td></tr>',
    )
    adapter = HtmlRowBackgroundColorAdapter()
    assert adapter.extract(tag) == "ffffbf"
