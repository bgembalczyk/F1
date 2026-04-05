"""Tests for low-coverage transformer modules."""

from __future__ import annotations

import pytest

from scrapers.base.transformers.fatalities_car import FatalitiesCarTransformer
from scrapers.base.transformers.failed_to_make_restart import (
    FailedToMakeRestartTransformer,
)
from scrapers.base.transformers.points_scoring_systems_history import (
    PointsScoringSystemsHistoryTransformer,
)
from scrapers.base.transformers.shortened_race_points import (
    ShortenedRacePointsTransformer,
)
from scrapers.points.helpers.parsers import extract_first_place_role, seasons_key


# ---------------------------------------------------------------------------
# points/helpers/parsers.py
# ---------------------------------------------------------------------------


def test_seasons_key_returns_none_for_empty() -> None:
    assert seasons_key(None) is None
    assert seasons_key([]) is None


def test_seasons_key_returns_tuple_of_year_url() -> None:
    seasons = [
        {"year": 2005, "url": "https://en.wikipedia.org/wiki/2005"},
        {"year": 2006, "url": "https://en.wikipedia.org/wiki/2006"},
    ]
    result = seasons_key(seasons)
    assert result == (
        (2005, "https://en.wikipedia.org/wiki/2005"),
        (2006, "https://en.wikipedia.org/wiki/2006"),
    )


def test_extract_first_place_role_returns_role_and_value() -> None:
    first_place = {"role": "driver", "value": 9}
    role, value = extract_first_place_role(first_place)
    assert role == "driver"
    assert value == 9


def test_extract_first_place_role_returns_none_role_when_no_role_key() -> None:
    role, value = extract_first_place_role({"other_key": 5})
    assert role is None
    assert value is None


def test_extract_first_place_role_returns_int_value_when_plain_int() -> None:
    role, value = extract_first_place_role(9)
    assert role is None
    assert value == 9


def test_extract_first_place_role_returns_none_for_non_int_non_dict() -> None:
    role, value = extract_first_place_role("8")
    assert role is None
    assert value is None


def test_extract_first_place_role_returns_none_for_none() -> None:
    role, value = extract_first_place_role(None)
    assert role is None
    assert value is None


# ---------------------------------------------------------------------------
# transformers/points_scoring_systems_history.py
# ---------------------------------------------------------------------------


def test_points_scoring_systems_history_transformer_plain_records() -> None:
    transformer = PointsScoringSystemsHistoryTransformer()
    records = [
        {"seasons": [{"year": 1950}], "1st": 8, "2nd": 6},
        {"seasons": [{"year": 1960}], "1st": 9, "2nd": 6},
    ]
    result = transformer.transform(records)
    assert len(result) == 2
    assert result[0]["1st"] == 8
    assert result[1]["1st"] == 9


def test_points_scoring_systems_history_transformer_merges_role_records() -> None:
    transformer = PointsScoringSystemsHistoryTransformer()
    seasons = [{"year": 2014, "url": "http://example.com/2014"}]
    records = [
        {"seasons": seasons, "1st": {"role": "driver", "value": 25}},
        {"seasons": seasons, "1st": {"role": "constructor", "value": 43}},
    ]
    result = transformer.transform(records)
    assert len(result) == 1
    merged_first = result[0]["1st"]
    assert merged_first["driver"] == 25
    assert merged_first["constructor"] == 43


def test_points_scoring_systems_history_transformer_handles_no_seasons() -> None:
    transformer = PointsScoringSystemsHistoryTransformer()
    records = [
        {"seasons": None, "1st": 10},
        {"seasons": None, "1st": 12},
    ]
    result = transformer.transform(records)
    # Both records map to key=None; the second is deduplicated
    assert len(result) == 1
    assert result[0]["1st"] == 10


def test_points_scoring_systems_history_transformer_skips_non_role_duplicates() -> None:
    transformer = PointsScoringSystemsHistoryTransformer()
    seasons = [{"year": 1950, "url": None}]
    records = [
        {"seasons": seasons, "1st": 8},
        {"seasons": seasons, "1st": 9},
    ]
    result = transformer.transform(records)
    # Second record is simply skipped (key already present)
    assert len(result) == 1
    assert result[0]["1st"] == 8


# ---------------------------------------------------------------------------
# transformers/shortened_race_points.py
# ---------------------------------------------------------------------------


def test_shortened_race_points_transformer_groups_by_seasons() -> None:
    transformer = ShortenedRacePointsTransformer()
    seasons_a = [{"year": 1950, "url": None}]
    seasons_b = [{"year": 1960, "url": None}]
    records = [
        {"seasons": seasons_a, "75%": 6, "50%": 4},
        {"seasons": seasons_a, "90%": 5},
        {"seasons": seasons_b, "75%": 8},
    ]
    result = transformer.transform(records)
    assert len(result) == 2

    group_a = next(r for r in result if r["seasons"] == seasons_a)
    assert len(group_a["race_length_points"]) == 2
    assert {"75%": 6, "50%": 4} in group_a["race_length_points"]

    group_b = next(r for r in result if r["seasons"] == seasons_b)
    assert len(group_b["race_length_points"]) == 1


def test_shortened_race_points_transformer_excludes_seasons_from_inner() -> None:
    transformer = ShortenedRacePointsTransformer()
    seasons = [{"year": 2021, "url": None}]
    records = [{"seasons": seasons, "75%": 12, "50%": 6}]
    result = transformer.transform(records)
    inner = result[0]["race_length_points"][0]
    assert "seasons" not in inner
    assert inner["75%"] == 12


def test_shortened_race_points_transformer_empty_input() -> None:
    transformer = ShortenedRacePointsTransformer()
    assert transformer.transform([]) == []


# ---------------------------------------------------------------------------
# transformers/fatalities_car.py
# ---------------------------------------------------------------------------


def test_fatalities_car_transformer_moves_formula_category_into_car_dict() -> None:
    transformer = FatalitiesCarTransformer()
    records = [
        {"car": {"text": "Ferrari", "url": None}, "formula_category": "F1"},
    ]
    result = transformer.transform(records)
    assert result[0]["car"] == {"text": "Ferrari", "url": None, "formula_category": "F1"}
    assert "formula_category" not in result[0]


def test_fatalities_car_transformer_wraps_plain_car_string() -> None:
    transformer = FatalitiesCarTransformer()
    records = [{"car": "Cooper", "formula_category": "F2"}]
    result = transformer.transform(records)
    assert result[0]["car"] == {"text": "Cooper", "url": None, "formula_category": "F2"}


def test_fatalities_car_transformer_skips_rows_without_formula_category() -> None:
    transformer = FatalitiesCarTransformer()
    records = [{"car": "BRM"}]
    result = transformer.transform(records)
    assert result[0]["car"] == "BRM"


def test_fatalities_car_transformer_handles_none_car_with_category() -> None:
    transformer = FatalitiesCarTransformer()
    records = [{"car": None, "formula_category": "F1"}]
    result = transformer.transform(records)
    assert result[0]["car"] == {"text": "", "url": None, "formula_category": "F1"}


def test_fatalities_car_transformer_empty_input() -> None:
    transformer = FatalitiesCarTransformer()
    assert transformer.transform([]) == []


# ---------------------------------------------------------------------------
# transformers/failed_to_make_restart.py
# ---------------------------------------------------------------------------


def test_failed_to_make_restart_transformer_merges_fields() -> None:
    transformer = FailedToMakeRestartTransformer()
    records = [
        {
            "failed_to_make_restart_drivers": ["Hamilton", "Vettel"],
            "failed_to_make_restart_reason": "accident",
        },
    ]
    result = transformer.transform(records)
    assert result[0]["failed_to_make_restart"] == {
        "drivers": ["Hamilton", "Vettel"],
        "reason": "accident",
    }
    assert "failed_to_make_restart_drivers" not in result[0]
    assert "failed_to_make_restart_reason" not in result[0]


def test_failed_to_make_restart_transformer_skips_rows_without_fields() -> None:
    transformer = FailedToMakeRestartTransformer()
    records = [{"some_key": "value"}]
    result = transformer.transform(records)
    assert "failed_to_make_restart" not in result[0]


def test_failed_to_make_restart_transformer_handles_none_drivers() -> None:
    transformer = FailedToMakeRestartTransformer()
    records = [
        {
            "failed_to_make_restart_drivers": None,
            "failed_to_make_restart_reason": "weather",
        },
    ]
    result = transformer.transform(records)
    assert result[0]["failed_to_make_restart"] == {
        "drivers": [],
        "reason": "weather",
    }


def test_failed_to_make_restart_transformer_empty_input() -> None:
    transformer = FailedToMakeRestartTransformer()
    assert transformer.transform([]) == []
