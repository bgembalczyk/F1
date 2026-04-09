from __future__ import annotations

import pytest

from scrapers.seasons.columns_seasons.helpers.race_result import rules


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (
            1960,
            {
                "shared_drive": True,
                "points_eligible": False,
                "notes": ["shared_drive_no_points"],
            },
        ),
        (1957, {"shared_drive": True, "points_shared": True}),
    ],
)
def test_shared_drive_rule_for_historical_windows(year: int, expected: dict) -> None:
    result = {"position": 2, "marks": ["†"]}
    rules.SharedDriveRule().apply(
        result,
        rules.ResultRuleContext(season_year=year, background=None, footnotes=[]),
    )

    for key, value in expected.items():
        assert result[key] == value


def test_shared_drive_rule_boundary_without_dagger_is_noop() -> None:
    result = {"position": 2, "marks": ["*"]}
    rules.SharedDriveRule().apply(
        result,
        rules.ResultRuleContext(season_year=1958, background=None, footnotes=[]),
    )
    assert result == {"position": 2, "marks": ["*"]}


def test_classified_dnf_rule_adds_note() -> None:
    result = {"position": 8, "marks": ["†"]}
    rules.ClassifiedDNFRule().apply(
        result,
        rules.ResultRuleContext(
            season_year=1985,
            background="Other classified position",
            footnotes=[],
        ),
    )
    assert "classified_after_dnf_90_percent" in result["notes"]


def test_fatal_accident_rule_boundary_non_string_position_is_noop() -> None:
    result = {"position": 1, "marks": ["†"]}
    rules.FatalAccidentRule().apply(
        result,
        rules.ResultRuleContext(season_year=1970, background=None, footnotes=[]),
    )
    assert "notes" not in result


def test_mark_based_eligibility_rule_sets_no_points_for_double_dagger_position() -> (
    None
):
    result = {"position": 5, "marks": ["‡"]}
    rules.MarkBasedEligibilityRule().apply(
        result,
        rules.ResultRuleContext(season_year=2000, background=None, footnotes=[]),
    )
    assert result["points_eligible"] is False
    assert "no_points_awarded" in result["notes"]


def test_star_mark_note_rule_boundary_wrong_background_is_noop() -> None:
    result = {"position": 3, "marks": ["*"]}
    rules.StarMarkNoteRule("special_note").apply(
        result,
        rules.ResultRuleContext(season_year=2000, background="Winner", footnotes=[]),
    )
    assert "notes" not in result


def test_half_points_round_rule_applies_and_skips_indianapolis_500() -> None:
    half_rule = rules.HalfPointsRoundRule()
    applies = half_rule.apply(
        rules.RoundRuleContext(
            season_year=1975,
            marks=["*"],
            header_text="Spanish Grand Prix",
            round_url="https://en.wikipedia.org/wiki/1975_Spanish_Grand_Prix",
        ),
    )
    blocked = half_rule.apply(
        rules.RoundRuleContext(
            season_year=1960,
            marks=["*"],
            header_text="500",
            round_url="https://en.wikipedia.org/wiki/Indianapolis_500",
        ),
    )

    assert applies == {"note": "half_points", "points_multiplier": 0.5}
    assert blocked is None


def test_double_points_round_rule_applies_only_for_2014_abu_dhabi_with_mark() -> None:
    rule = rules.DoublePointsRoundRule()

    assert rule.apply(
        rules.RoundRuleContext(
            season_year=2014,
            marks=["‡"],
            header_text="Abu Dhabi",
            round_url="https://en.wikipedia.org/wiki/2014_Abu_Dhabi_Grand_Prix",
        ),
    ) == {"note": "double_points", "points_multiplier": 2.0}
    assert (
        rule.apply(
            rules.RoundRuleContext(
                season_year=2015,
                marks=["‡"],
                header_text="Abu Dhabi",
                round_url="https://en.wikipedia.org/wiki/2015_Abu_Dhabi_Grand_Prix",
            ),
        )
        is None
    )
