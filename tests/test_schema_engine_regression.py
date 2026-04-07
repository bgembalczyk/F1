from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from validation.issue import IssueMessageFormatter
from validation.issue import LegacyValidationIssueAdapter
from validation.issue import ValidationIssue
from validation.record_validation import validate_record
from validation.schema_rules import build_domain_rules
from validation.schema_engine import SchemaValidationEngine
from validation.schemas import NestedSchema
from validation.schemas import RecordSchema

INVALID_TEAM_VALUE = 7


def _legacy_coerce_issue(error: ValidationIssue | str) -> ValidationIssue:
    if isinstance(error, ValidationIssue):
        return error
    message = str(error)
    missing_key = SchemaValidationEngine.extract_missing_key(message)
    if missing_key:
        code = "null" if message.startswith("Null value for: ") else "missing"
        return ValidationIssue(code=code, field=missing_key, message=message)
    type_key = SchemaValidationEngine.extract_type_key(message)
    if type_key:
        return ValidationIssue(code="type", field=type_key, message=message)
    return ValidationIssue.custom(message)


def _legacy_prefix_errors(
    errors: list[ValidationIssue],
    prefix: str,
) -> list[ValidationIssue]:
    return [error.with_prefix(prefix) for error in errors]


def _legacy_validate_nested_schema(
    record: Mapping[str, Any],
    nested_schema: RecordSchema,
) -> list[ValidationIssue]:
    return _legacy_validate_schema(record, nested_schema)


def _legacy_validate_nested_value(
    key: str,
    value: Any,
    nested_schema: NestedSchema,
) -> list[ValidationIssue]:
    errors: list[ValidationIssue] = []
    if nested_schema.is_list:
        if not isinstance(value, list):
            errors.append(ValidationIssue.type_error(key, "list", type(value).__name__))
            return errors
        for index, item in enumerate(value):
            if not isinstance(item, Mapping):
                errors.append(
                    ValidationIssue.custom(f"{key}[{index}] must be a mapping"),
                )
                continue
            errors.extend(
                _legacy_prefix_errors(
                    _legacy_validate_nested_schema(item, nested_schema.schema),
                    f"{key}[{index}]",
                ),
            )
        return errors

    if not isinstance(value, Mapping):
        return [ValidationIssue.custom(f"{key} must be a mapping")]

    return _legacy_prefix_errors(
        _legacy_validate_nested_schema(value, nested_schema.schema),
        key,
    )


def _legacy_validate_schema(
    record: Mapping[str, Any],
    schema: RecordSchema,
) -> list[ValidationIssue]:
    errors: list[ValidationIssue] = []
    allow_none = set(schema.allow_none)
    errors.extend(_legacy_missing_required_errors(record, schema))
    errors.extend(_legacy_type_errors(record, schema, allow_none))
    errors.extend(_legacy_nested_errors(record, schema))
    errors.extend(_legacy_custom_validator_errors(record, schema))
    return [IssueMessageFormatter.render(e) for e in errors]


def _legacy_missing_required_errors(
    record: Mapping[str, Any],
    schema: RecordSchema,
) -> list[ValidationIssue]:
    return [
        ValidationIssue.missing(key) for key in schema.required if key not in record
    ]


def _legacy_type_errors(
    record: Mapping[str, Any],
    schema: RecordSchema,
    allow_none: set[str],
) -> list[ValidationIssue]:
    errors: list[ValidationIssue] = []
    for key, expected_types in schema.types.items():
        if key not in record:
            errors.append(ValidationIssue.missing(key))
            continue
        value = record[key]
        if value is None:
            if key not in allow_none:
                errors.append(ValidationIssue.null(key))
            continue
        if isinstance(value, expected_types):
            continue
        expected = (
            expected_types if isinstance(expected_types, tuple) else (expected_types,)
        )
        expected_names = ", ".join(value_type.__name__ for value_type in expected)
        errors.append(
            ValidationIssue.type_error(key, expected_names, type(value).__name__),
        )
    return errors


def _legacy_nested_errors(
    record: Mapping[str, Any],
    schema: RecordSchema,
) -> list[ValidationIssue]:
    errors: list[ValidationIssue] = []
    for key, nested_schema in schema.nested.items():
        if key not in record:
            continue
        value = record[key]
        if value is None:
            continue
        errors.extend(_legacy_validate_nested_value(key, value, nested_schema))
    return errors


def _legacy_custom_validator_errors(
    record: Mapping[str, Any],
    schema: RecordSchema,
) -> list[ValidationIssue]:
    errors: list[ValidationIssue] = []
    for validator in schema.custom_validators:
        errors.extend(_legacy_coerce_issue(error) for error in validator(record))
    return errors


class LegacyNestedRule:
    def __init__(self, schema: RecordSchema):
        self.schema = schema

    def __call__(self, record: Mapping[str, Any]) -> list[ValidationIssue]:
        return _legacy_nested_errors(record, self.schema)


class LegacyCustomRule:
    def __init__(self, schema: RecordSchema):
        self.schema = schema

    def __call__(self, record: Mapping[str, Any]) -> list[ValidationIssue]:
        return _legacy_custom_validator_errors(record, self.schema)


def _legacy_build_domain_rules(schema: RecordSchema):
    return [LegacyNestedRule(schema), LegacyCustomRule(schema)]


def _sample_schema() -> RecordSchema:
    season_schema = RecordSchema(required=("year",), types={"year": int})
    profile_schema = RecordSchema(required=("country",), types={"country": str})

    def custom_validator(record: Mapping[str, Any]) -> list[ValidationIssue | str]:
        errors: list[ValidationIssue | str] = []
        if record.get("status") is None:
            errors.append("Null value for: status")
        if record.get("team") == INVALID_TEAM_VALUE:
            errors.append("Invalid type for team: expected str, got int")
        return errors

    return RecordSchema(
        required=("name",),
        types={"name": str, "status": str},
        nested={
            "profile": NestedSchema(schema=profile_schema),
            "seasons": NestedSchema(schema=season_schema, is_list=True),
        },
        custom_validators=(custom_validator,),
    )


def test_validate_schema_matches_legacy_behavior() -> None:
    schema = _sample_schema()
    record = {
        "name": 123,
        "status": None,
        "profile": {"country": 55},
        "seasons": [{"year": "2024"}, "broken"],
        "team": INVALID_TEAM_VALUE,
    }

    expected = _legacy_validate_schema(record, schema)
    actual = validate_record(record, schema)

    assert actual == expected


def test_build_domain_rules_matches_legacy_behavior() -> None:
    schema = _sample_schema()
    record = {
        "name": "Driver",
        "status": None,
        "profile": {"country": 55},
        "seasons": [{"year": "2024"}, "broken"],
        "team": INVALID_TEAM_VALUE,
    }

    legacy_errors: list[ValidationIssue] = []
    for rule in _legacy_build_domain_rules(schema):
        legacy_errors.extend(rule(record))

    new_errors: list[ValidationIssue] = []
    for rule in build_domain_rules(schema):
        new_errors.extend(rule(record))

    assert new_errors == legacy_errors
