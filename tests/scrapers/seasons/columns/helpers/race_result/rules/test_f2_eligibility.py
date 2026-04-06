from __future__ import annotations

from scrapers.seasons.columns.helpers.race_result.rules.context import ResultRuleContext
from scrapers.seasons.columns.helpers.race_result.rules.f2_eligibility import (
    F2EligibilityRule,
)


def test_f2_eligibility_marks_driver_ineligible_in_f2_year_with_footnote_1() -> None:
    result = {"position": 2}
    context = ResultRuleContext(
        season_year=1957,
        background=None,
        footnotes=["1", "3"],
    )

    F2EligibilityRule().apply(result, context)

    assert result["points_eligible"] is False
    assert "ineligible_f2" in result["notes"]


def test_f2_eligibility_boundary_no_footnote_one_leaves_result_unchanged() -> None:
    result = {"position": 1}
    context = ResultRuleContext(
        season_year=1957,
        background=None,
        footnotes=["2"],
    )

    F2EligibilityRule().apply(result, context)

    assert result == {"position": 1}
