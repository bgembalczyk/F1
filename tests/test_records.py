from models.records import (
    CircuitCompleteRecord,
    CircuitDetailsRecord,
    CircuitRecord,
    DriverRecord,
    DriversChampionshipsRecord,
    LinkRecord,
    SeasonRecord,
)
from models.mappers.field_aliases import apply_field_aliases, FIELD_ALIASES
from models.records.driver import DRIVER_SCHEMA
from models.records.season import SEASON_SCHEMA
from validation.records import RecordValidator


def test_link_and_season_records_have_expected_keys() -> None:
    assert LinkRecord.__required_keys__ == {"text", "url"}
    assert SeasonRecord.__required_keys__ == {"year", "url"}


def test_driver_record_structure() -> None:
    assert DriverRecord.__required_keys__ == {
        "driver",
        "is_active",
        "is_world_champion",
        "nationality",
        "seasons_competed",
        "drivers_championships",
    }
    assert DriverRecord.__optional_keys__ == {
        "race_entries",
        "race_starts",
        "pole_positions",
        "race_wins",
        "podiums",
        "fastest_laps",
        "points",
    }
    assert DriversChampionshipsRecord.__required_keys__ == {"count", "seasons"}


def test_circuit_record_structure() -> None:
    assert CircuitRecord.__required_keys__ == {
        "circuit",
        "circuit_status",
        "type",
        "direction",
        "location",
        "country",
        "last_length_used_km",
        "last_length_used_mi",
        "turns",
        "grands_prix",
        "seasons",
        "grands_prix_held",
    }


def test_circuit_details_and_complete_records() -> None:
    assert CircuitDetailsRecord.__required_keys__ == {"url", "infobox", "tables"}
    assert CircuitCompleteRecord.__optional_keys__ >= {
        "name",
        "url",
        "circuit_status",
        "type",
        "direction",
        "grands_prix",
        "seasons",
        "grands_prix_held",
        "location",
        "fia_grade",
        "history",
        "layouts",
    }


def test_validate_schema_reports_missing_and_type_errors() -> None:
    errors = RecordValidator.validate_schema({"year": "2024"}, SEASON_SCHEMA)

    messages = [error.message for error in errors]
    assert "Missing key: url" in messages
    assert "Invalid type for year: expected int, got str" in messages


def test_validate_schema_handles_nested_records() -> None:
    record = {
        "driver": {"text": " ", "url": "https://example.com"},
        "nationality": "Polish",
        "seasons_competed": [{"year": "2024", "url": "https://example.com"}],
        "drivers_championships": {
            "count": 1,
            "seasons": [{"year": 2020, "url": "https://example.com"}],
        },
        "is_active": True,
        "is_world_champion": False,
    }

    errors = RecordValidator.validate_schema(record, DRIVER_SCHEMA)

    messages = [error.message for error in errors]
    assert "driver.text must be a non-empty string" in messages
    assert (
        "Invalid type for seasons_competed[0].year: expected int, got str" in messages
    )


def test_apply_field_aliases_resolves_constructor_wcc_wdc() -> None:
    payload = apply_field_aliases(
        {"wcc": 3, "wdc": 2},
        FIELD_ALIASES["constructor"],
        record_name="constructor",
    )

    assert payload["wcc_titles"] == 3
    assert payload["wdc_titles"] == 2


def test_apply_field_aliases_raises_on_conflict() -> None:
    try:
        apply_field_aliases(
            {"wcc": 2, "wcc_titles": 1},
            FIELD_ALIASES["constructor"],
            record_name="constructor",
        )
    except ValueError as exc:
        assert "Konflikt aliasów" in str(exc)
    else:
        raise AssertionError("Expected conflict error for alias mapping")
