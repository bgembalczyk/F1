from dataclasses import dataclass

import pytest

from models.validation.helpers import validate_float
from models.validation.helpers import validate_int
from models.validation.validators import model_to_dict
from models.validation.validators import normalize_link_list
from models.validation.validators import normalize_season_list
from models.validation.validators import validate_link
from models.validation.validators import validate_links
from models.validation.validators import validate_seasons
from models.value_objects.link import Link
from models.value_objects.season_ref import SeasonRef
from validation.issue import ValidationIssue
from validation.validator_base import RecordValidator

VALID_FLOAT_STRING = "3.5"
EXPECTED_FLOAT_VALUE = 3.5


def test_validate_int_allows_none_and_rejects_invalid_values():
    assert validate_int(None, "value") is None

    with pytest.raises(ValueError, match="musi być liczbą"):
        validate_int("bad", "value")

    with pytest.raises(ValueError, match="nie może być ujemne"):
        validate_int(-1, "value")


def test_validate_float_coerces_and_rejects_negative_values():
    assert validate_float(VALID_FLOAT_STRING, "value") == EXPECTED_FLOAT_VALUE

    with pytest.raises(ValueError, match="nie może być ujemne"):
        validate_float(-1.0, "value")


def test_validate_link_accepts_link_instance():
    link = Link(text="Example", url="https://example.com")

    assert validate_link(link, field_name="link") == link.to_dict()


def test_validate_links_filters_empty_entries():
    links = validate_links(
        [
            Link(),
            {"text": "Example", "url": "https://example.com"},
        ],
        field_name="links",
    )

    assert links == [{"text": "Example", "url": "https://example.com"}]


def test_validate_seasons_rejects_invalid_url():
    with pytest.raises(ValueError, match="Pole seasons zawiera nieprawidłowy URL"):
        validate_seasons([{"year": 2024, "url": "bad-url"}])


def test_model_to_dict_supports_multiple_model_shapes():
    class DumpModel:
        def model_dump(self):
            return {"source": "dump"}

    class DictModel:
        def dict(self):
            return {"source": "dict"}

    @dataclass
    class DataClassModel:
        value: int

    assert model_to_dict(DumpModel()) == {"source": "dump"}
    assert model_to_dict(DictModel()) == {"source": "dict"}
    assert model_to_dict(DataClassModel(value=1)) == {"value": 1}

    with pytest.raises(TypeError, match="Nieobsługiwany typ modelu"):
        model_to_dict(123)


def test_normalize_link_list_filters_empty_links():
    links = normalize_link_list(
        [
            {"text": "", "url": None},
            {"text": "Example", "url": None},
        ],
    )

    assert links == [Link(text="Example", url=None)]


def test_normalize_season_list_filters_none_entries():
    seasons = normalize_season_list(
        [
            {"year": 2020},
            {"url": "https://example.com"},
            SeasonRef(year=2021),
        ],
    )

    assert seasons == [SeasonRef(year=2020), SeasonRef(year=2021)]


def test_record_validator_checks_required_and_type_rules():
    record = {"name": "Example", "count": "invalid"}

    errors = RecordValidator.require_keys(
        record,
        ["name", "count", "missing"],
    )

    messages = [error.message for error in errors]
    assert "Missing key: missing" in messages
    type_messages = [
        error.message
        for error in RecordValidator.require_type(record, "count", int)
    ]
    assert "Invalid type for count: expected int, got str" in type_messages


def test_record_validator_link_helpers_report_invalid_entries():
    errors = RecordValidator.require_link_dict(
        {"text": " ", "url": 123},
        "link",
    )
    messages = [error.message for error in errors]
    assert "link.text must be a non-empty string" in messages
    assert "link.url must be a string or None" in messages

    list_errors = RecordValidator.require_link_list(
        [{"text": "Ok", "url": None}, "bad"],
        "links",
    )
    list_messages = [error.message for error in list_errors]
    assert "links[1] must be a link dict" in list_messages


def test_quality_report_tracks_structured_issues():
    class DummyValidator(RecordValidator):
        def validate(self, _record):  # type: ignore[override]
            return []

    validator = DummyValidator()
    validator.record_validation_result(
        [
            ValidationIssue.missing("name"),
            ValidationIssue.type_error("age", "int", "str"),
            ValidationIssue.custom("other issue"),
        ],
    )

    report = validator.build_quality_report()

    assert report["summary"]["total_records"] == 1
    assert report["summary"]["rejected_records"] == 1
    assert report["missing"] == {"name": 1}
    assert report["types"] == {"age": 1}
