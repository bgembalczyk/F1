# ruff: noqa: E501, PLR2004, RUF001, RUF002, RUF003, SLF001, ARG001, ARG002, N802, B017, PT011, PT017, E402, PT001, PLC0415, RUF100
import pytest

from models.records.factories.build import RECORD_BUILDERS
from models.records.factories.build import build_constructor_record
from models.records.factories.build import build_driver_record
from models.records.factories.build import build_fatality_record
from models.records.factories.build import build_grands_prix_record
from models.records.factories.build import build_record
from models.records.factories.build import build_season_record
from models.records.factories.build import build_season_summary_record
from models.records.factories.build import build_special_driver_record


def test_build_season_record_adds_url() -> None:
    record = build_season_record({"year": "2021"})
    assert record["year"] == 2021
    assert (
        record["url"]
        == "https://en.wikipedia.org/wiki/2021_Formula_One_World_Championship"
    )


def test_build_driver_record_normalizes_championships_and_seasons() -> None:
    record = build_driver_record(
        {
            "driver": {"text": "Test Driver", "url": ""},
            "nationality": " Polish ",
            "is_active": True,
            "is_world_champion": False,
            "seasons_competed": [{"year": "2003"}],
            "drivers_championships": {"count": "2", "seasons": [{"year": 2005}]},
        },
    )
    assert record["driver"]["text"] == "Test Driver"
    assert record["driver"]["url"] is None
    assert record["nationality"] == "Polish"
    assert record["drivers_championships"]["count"] == 2
    assert record["seasons_competed"][0]["year"] == 2003


def test_build_constructor_record_normalizes_links_and_numbers() -> None:
    record = build_constructor_record(
        {
            "constructor": {"text": "Test Team", "url": "https://example.com"},
            "engine": [{"text": "Engine", "url": "https://example.com/engine"}],
            "based_in": [{"text": "UK", "url": None}],
            "seasons": [{"year": 2000}],
            "antecedent_teams": [],
            "wcc_titles": "3",
        },
    )
    assert record["constructor"]["text"] == "Test Team"
    assert record["seasons"][0]["url"].endswith("2000_Formula_One_World_Championship")
    assert record["wcc_titles"] == 3


def test_build_special_driver_record_normalizes_points_and_entries() -> None:
    record = build_special_driver_record(
        {
            "driver": {"text": "Test Driver", "url": "https://example.com/driver"},
            "seasons": [{"year": "1999"}],
            "teams": [{"text": "Test Team", "url": "https://example.com/team"}],
            "entries": "5",
            "starts": "3",
            "points": {"championship_points": "1.5", "total_points": "2"},
        },
    )
    assert record["entries"] == 5
    assert record["starts"] == 3
    assert record["points"]["championship_points"] == 1.5
    assert record["points"]["total_points"] == 2.0


def test_build_grands_prix_record_normalizes_seasons_and_totals() -> None:
    record = build_grands_prix_record(
        {
            "race_title": {"text": "Test Grand Prix", "url": "https://example.com/gp"},
            "race_status": "active",
            "years_held": [{"year": "1950"}],
            "country": [{"text": "Country", "url": "https://example.com/country"}],
            "total": "24",
        },
    )
    assert record["years_held"][0]["year"] == 1950
    assert record["total"] == 24


def test_build_fatality_record_normalizes_event_and_car() -> None:
    record = build_fatality_record(
        {
            "driver": {"text": "Test Driver", "url": "https://example.com/driver"},
            "date": "1960-01-01",
            "age": "30",
            "event": {
                "event": {"text": "Test GP", "url": "https://example.com/gp"},
                "championship": False,
            },
            "circuit": {"text": "Test Circuit", "url": "https://example.com/circuit"},
            "car": {
                "text": "Test Car",
                "url": "https://example.com/car",
                "formula_category": " F1 ",
            },
            "session": "Race",
        },
    )
    assert record["age"] == 30
    assert record["event"]["championship"] is False
    assert record["car"]["formula_category"] == "F1"


def test_build_season_summary_record_normalizes_links() -> None:
    record = build_season_summary_record(
        {
            "season": {"text": "2020", "url": "https://example.com/season"},
            "races": "17",
            "countries": "10",
            "drivers_champion_team": [
                {"text": "Driver", "url": "https://example.com/driver"},
            ],
            "constructors_champion": [
                {"text": "Team", "url": "https://example.com/team"},
            ],
            "winners": "9",
        },
    )
    assert record["races"] == 17
    assert record["countries"] == 10
    assert record["winners"] == 9


def test_build_record_uses_registry() -> None:
    record = build_record("season", {"year": "2022"})
    assert record["year"] == 2022


def test_build_record_raises_for_unsupported_type() -> None:
    with pytest.raises(ValueError, match="Unsupported record type"):
        build_record("unknown", {})


def test_record_builders_facade_supports_typed_and_generic_builds() -> None:
    season_record = RECORD_BUILDERS.season({"year": "2023"})
    generic_record = RECORD_BUILDERS.build("season", {"year": "2024"})

    assert season_record["year"] == 2023
    assert generic_record["year"] == 2024


def test_record_builders_facade_raises_for_unsupported_type() -> None:
    with pytest.raises(ValueError, match="Unsupported record type"):
        RECORD_BUILDERS.build("unknown", {})
