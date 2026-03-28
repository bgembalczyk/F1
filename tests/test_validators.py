import pytest

from models.validation.helpers import validate_float
from models.validation.helpers import validate_int
from models.validation.helpers import validate_status
from models.validation.validators import validate_seasons
from models.value_objects.link_utils import validate_link
from models.value_objects.season_ref import SeasonRef
from validation.issue import ValidationIssue
from validation.validator_base import RecordValidator

VALID_FLOAT_STRING = "3.5"
EXPECTED_FLOAT_VALUE = 3.5


def test_validate_link_accepts_link_dict():
    link = validate_link(
        {"text": "Site", "url": "https://example.com"},
        field_name="link",
    )

    assert link == {"text": "Site", "url": "https://example.com"}


def test_validate_link_accepts_none_payload():
    link = validate_link(None, field_name="link")

    assert link == {"text": "", "url": None}


def test_validate_link_accepts_empty_payload():
    link = validate_link({"text": " ", "url": ""}, field_name="link")

    assert link == {"text": "", "url": None}


def test_validate_link_rejects_invalid_url():
    with pytest.raises(ValueError, match="nieprawidłowy URL"):
        validate_link({"text": "Bad", "url": "notaurl"}, field_name="link")


def test_validate_seasons_filters_empty_and_coerces():
    seasons = validate_seasons(
        [
            {"year": 2020, "url": "https://example.com"},
            {"year": None},
            SeasonRef(year=2021),
        ],
    )

    assert seasons == [
        {"year": 2020, "url": "https://example.com"},
        {"year": 2021},
    ]


def test_validate_seasons_handles_empty_input():
    assert validate_seasons(None) == []


def test_validate_status_normalizes_case():
    assert validate_status(" Current ", ["current", "former"], "status") == "current"


def test_validate_status_rejects_unknown_value():
    with pytest.raises(ValueError, match="musi mieć jedną z wartości"):
        validate_status("unknown", ["current", "former"], "status")


def test_validate_int_rejects_negative_values():
    with pytest.raises(ValueError, match="nie może być ujemne"):
        validate_int(-1, "value")


def test_validate_float_accepts_numeric_strings():
    assert validate_float(VALID_FLOAT_STRING, "value") == EXPECTED_FLOAT_VALUE


def test_quality_report_counts_null_fields():
    class DummyValidator(RecordValidator):
        def validate(self, _record):  # type: ignore[override]
            return []

    validator = DummyValidator()
    validator.record_validation_result([ValidationIssue.null("driver")])

    report = validator.build_quality_report()

    assert report["summary"]["total_records"] == 1
    assert report["summary"]["rejected_records"] == 1
    assert report["missing"] == {"driver": 1}
