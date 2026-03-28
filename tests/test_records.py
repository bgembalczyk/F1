# ruff: noqa: E501, PLR2004, RUF001, RUF002, RUF003, SLF001, ARG001, ARG002, N802, B017, PT011, PT017, E402, PT001, PLC0415, RUF100
from models.mappers.field_aliases import FIELD_ALIASES
from models.mappers.field_aliases import apply_field_aliases
from models.mappers.serialization import to_circuit_record_dict
from models.records.circuit import CIRCUIT_DEFINITION
from models.records.circuit import CircuitRecord
from models.records.circuit import validate_circuit_record
from models.records.circuit_base import CircuitBaseRecord
from models.records.circuit_complete import CircuitCompleteRecord
from models.records.circuit_complete import validate_circuit_complete_record
from models.records.circuit_details import CircuitDetailsRecord
from models.records.circuit_details import validate_circuit_details_record
from models.records.constructor import CONSTRUCTOR_DEFINITION
from models.records.constructor import ConstructorRecord
from models.records.constructor import validate_constructor_record
from models.records.driver import DRIVER_DEFINITION
from models.records.driver import DRIVER_SCHEMA
from models.records.driver import DriverRecord
from models.records.driver import validate_driver_record
from models.records.driver_championships import DriversChampionshipsRecord
from models.records.link import LinkRecord
from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.validator_base import RecordValidator


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
    assert CircuitBaseRecord.__required_keys__ == set()
    assert CircuitBaseRecord.__optional_keys__ == {"url"}
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


def test_validate_circuit_base_in_details_and_complete() -> None:
    details_errors = validate_circuit_details_record(
        {"url": None, "infobox": {}, "tables": []},
    )
    complete_errors = validate_circuit_complete_record({"url": None})

    assert "Null value for: url" in details_errors
    assert complete_errors == []


def test_circuit_serialization_supports_details_and_complete() -> None:
    details = {"url": "https://example.com", "infobox": {}, "tables": []}
    complete = {"url": None, "grands_prix": [], "seasons": []}

    assert to_circuit_record_dict(details)["url"] == "https://example.com"
    assert to_circuit_record_dict(complete)["url"] is None


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
        msg = "Expected conflict error for alias mapping"
        raise AssertionError(msg)


def test_record_definition_consistency_for_core_typeddicts() -> None:
    metadata = (
        (DriverRecord, DRIVER_DEFINITION, validate_driver_record),
        (ConstructorRecord, CONSTRUCTOR_DEFINITION, validate_constructor_record),
        (CircuitRecord, CIRCUIT_DEFINITION, validate_circuit_record),
    )

    for typed_dict, definition, validator in metadata:
        assert definition.name
        assert definition.to_schema().required
        assert callable(validator)
        assert validator({})
        assert set(definition.required).issubset(set(typed_dict.__annotations__))
