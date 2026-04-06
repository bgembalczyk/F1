import json

from models.records.event import EVENT_SCHEMA
from models.records.event import EventRecord
from models.records.event import validate_event_field
from validation.record_validation import validate_record


def test_event_record_accepts_full_payload_with_link_mapping() -> None:
    record: EventRecord = {
        "event": {"text": "Monaco Grand Prix", "url": "https://example.com/monaco"},
        "championship": True,
    }

    errors = validate_record(record, EVENT_SCHEMA)

    assert errors == []


def test_event_record_accepts_partial_payload_with_only_championship() -> None:
    record: EventRecord = {"championship": False}

    errors = validate_record(record, EVENT_SCHEMA)

    assert errors == []


def test_event_optional_field_normalization_accepts_none_and_missing_value() -> None:
    assert validate_event_field({"event": None}) == []
    assert validate_event_field({}) == []


def test_event_field_supports_string_or_list_of_links_and_reports_invalid_items(
) -> None:
    assert validate_event_field({"event": "Goodwood Festival"}) == []

    errors = validate_event_field(
        {
            "event": [
                {"text": "Race of Champions", "url": "https://example.com/roc"},
                "unexpected",
            ],
        },
    )

    assert len(errors) == 1
    assert errors[0].message == "event[1] must be a mapping"


def test_event_record_representation_and_serialization_are_plain_json_friendly(
) -> None:
    record: EventRecord = {
        "event": "Mille Miglia",
        "championship": False,
    }

    assert "Mille Miglia" in repr(record)
    assert json.loads(json.dumps(record)) == record
