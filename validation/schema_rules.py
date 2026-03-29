"""Helpers that convert ``RecordSchema`` into composable rule lists."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from validation.issue import ValidationIssue
from validation.schema_engine import SchemaValidationEngine
from validation.schemas import RecordSchema

if TYPE_CHECKING:
    from collections.abc import Mapping

    from validation.rules import ValidationRule


def _coerce_schema(schema: RecordSchema | Mapping[str, Any]) -> RecordSchema:
    return SchemaValidationEngine.coerce_schema(schema)


def _coerce_issue(error: ValidationIssue | str) -> ValidationIssue:
    return SchemaValidationEngine.coerce_issue(error)


def _schema_validator(
    record: Mapping[str, Any],
    schema: RecordSchema | Mapping[str, Any],
) -> list[ValidationIssue]:
    from validation.validator_base import RecordValidator

    return RecordValidator.validate_schema(record, schema)


def build_domain_rules(
    schema: RecordSchema | Mapping[str, Any],
) -> list[ValidationRule]:
    normalized = _coerce_schema(schema)

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
                    _schema_validator,
                ),
            )
        return errors

    def _custom_rule(record: Mapping[str, Any]) -> list[ValidationIssue]:
        errors: list[ValidationIssue] = []
        for validator in normalized.custom_validators:
            errors.extend(_coerce_issue(error) for error in validator(record))
        return errors

    return [_nested_rule, _custom_rule]
