"""Single entrypoint for validating raw records against schemas."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from validation.issue import ValidationIssue
from validation.schema_engine import SchemaValidationEngine

if TYPE_CHECKING:
    from collections.abc import Mapping

    from validation.schemas import NestedSchema
    from validation.schemas import RecordSchema


def validate_record(
    record: Mapping[str, Any],
    schema: RecordSchema | Mapping[str, Any],
) -> list[ValidationIssue]:
    normalized = SchemaValidationEngine.coerce_schema(schema)
    errors: list[ValidationIssue] = []
    errors.extend(_require_keys(record, normalized.required))
    allow_none = set(normalized.allow_none)
    for key, expected_types in normalized.types.items():
        errors.extend(
            _require_type(
                record,
                key,
                expected_types,
                allow_none=key in allow_none,
            ),
        )
    for key, nested_schema in normalized.nested.items():
        if key not in record:
            continue
        value = record[key]
        if value is None:
            continue
        errors.extend(_validate_nested_value(key, value, nested_schema))
    for validator in normalized.custom_validators:
        errors.extend(
            SchemaValidationEngine.coerce_issue(error) for error in validator(record)
        )
    return SchemaValidationEngine.render_issues(errors)


def _validate_nested_value(
    key: str,
    value: Any,
    nested_schema: NestedSchema,
) -> list[ValidationIssue]:
    return SchemaValidationEngine.validate_nested_value(
        key,
        value,
        nested_schema,
        validate_record,
    )


def _require_keys(
    record: Mapping[str, Any],
    keys: tuple[str, ...],
) -> list[ValidationIssue]:
    return [ValidationIssue.missing(key) for key in keys if key not in record]


def _require_type(
    record: Mapping[str, Any],
    key: str,
    expected_types: type | tuple[type, ...],
    *,
    allow_none: bool = False,
) -> list[ValidationIssue]:
    if key not in record:
        return []

    value = record[key]
    if value is None:
        return [] if allow_none else [ValidationIssue.null(key)]

    if isinstance(value, expected_types):
        return []

    expected = (
        expected_types if isinstance(expected_types, tuple) else (expected_types,)
    )
    expected_names = ", ".join(value_type.__name__ for value_type in expected)
    return [
        ValidationIssue.type_error(
            key,
            expected_names,
            type(value).__name__,
        ),
    ]
