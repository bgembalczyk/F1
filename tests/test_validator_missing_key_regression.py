from validation.issue import ValidationIssue
from validation.record_validation import validate_record
from validation.validator_base import RecordValidator


def test_validate_schema_reports_single_missing_error_for_typed_missing_field() -> None:
    errors = validate_record(
        {"name": "Example"},
        {
            "required": ("name", "count"),
            "types": {"count": int},
        },
    )

    assert errors == [ValidationIssue.missing("count")]


def test_quality_report_maintains_missing_and_types_buckets() -> None:
    class DummyValidator(RecordValidator):
        def validate(self, _record):  # type: ignore[override]
            return []

    validator = DummyValidator()
    errors = validate_record(
        {"name": "Example"},
        {
            "required": ("name", "count"),
            "types": {"count": int, "name": int},
        },
    )
    validator.record_validation_result(errors)

    report = validator.build_quality_report()
    assert report["missing"] == {"count": 1}
    assert report["types"] == {"name": 1}
