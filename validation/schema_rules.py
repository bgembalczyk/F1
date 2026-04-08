"""Helpers that convert ``RecordSchema`` into composable rule lists."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from validation.record_validation import validate_record
from validation.schema_engine import SchemaValidationEngine

if TYPE_CHECKING:
    from collections.abc import Mapping

    from validation.issue import ValidationIssue
    from validation.rules import ValidationRule
    from validation.schemas import RecordSchema


def coerce_schema(schema: RecordSchema | Mapping[str, Any]) -> RecordSchema:
    return SchemaValidationEngine.coerce_schema(schema)


def coerce_issue(error: ValidationIssue | str) -> ValidationIssue:
    return SchemaValidationEngine.coerce_issue(error)


def schema_validator(
    record: Mapping[str, Any],
    schema: RecordSchema | Mapping[str, Any],
) -> list[ValidationIssue]:
    return validate_record(record, schema)


def build_domain_rules(
    schema: RecordSchema | Mapping[str, Any],
) -> list[ValidationRule]:
    normalized = coerce_schema(schema)

    def _nested_rule(record: Mapping[str, Any]) -> list[ValidationIssue]:
        errors: list[ValidationIssue] = []
        for key, nested_schema in normalized.nested.items():
            if key not in record:
                continue
            value = record[key]
            if value is None:
                continue
            errors.extend(
                SchemaValidationEngine.validate_nested_value(
                    key,
                    value,
                    nested_schema,
                    schema_validator,
                ),
            )
        return errors

    def _custom_rule(record: Mapping[str, Any]) -> list[ValidationIssue]:
        errors: list[ValidationIssue] = []
        for validator in normalized.custom_validators:
            errors.extend(coerce_issue(error) for error in validator(record))
        return errors

    return [_nested_rule, _custom_rule]


__all__ = [
    "build_domain_rules",
    "coerce_schema",
    "coerce_issue",
    "schema_validator",
]
