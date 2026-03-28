"""Helpers that convert ``RecordSchema`` into composable rule lists."""

from __future__ import annotations

from collections.abc import Mapping as MappingABC
from typing import TYPE_CHECKING
from typing import Any

from validation.issue import ValidationIssue
from validation.schemas import RecordSchema
from validation.validator_base import RecordValidator

if TYPE_CHECKING:
    from collections.abc import Mapping

    from validation.rules import ValidationRule
    from validation.schemas import NestedSchema


def _coerce_schema(schema: RecordSchema | Mapping[str, Any]) -> RecordSchema:
    if isinstance(schema, RecordSchema):
        return schema
    return RecordSchema(
        required=schema.get("required", ()),
        types=schema.get("types", {}),
        allow_none=schema.get("allow_none", ()),
        nested=schema.get("nested", {}),
        custom_validators=schema.get("custom_validators", ()),
    )


def _coerce_issue(error: ValidationIssue | str) -> ValidationIssue:
    if isinstance(error, ValidationIssue):
        return error
    return ValidationIssue.custom(str(error))


def _validate_nested_field(
    key: str,
    value: Any,
    nested_schema: NestedSchema,
) -> list[ValidationIssue]:
    errors: list[ValidationIssue] = []
    if nested_schema.is_list:
        if not isinstance(value, list):
            return [ValidationIssue.type_error(key, "list", type(value).__name__)]
        for index, item in enumerate(value):
            if not isinstance(item, MappingABC):
                errors.append(
                    ValidationIssue.custom(f"{key}[{index}] must be a mapping"),
                )
                continue
            errors.extend(
                RecordValidator.prefix_errors(
                    RecordValidator.validate_schema(item, nested_schema.schema),
                    f"{key}[{index}]",
                ),
            )
        return errors

    if not isinstance(value, MappingABC):
        return [ValidationIssue.custom(f"{key} must be a mapping")]

    return RecordValidator.prefix_errors(
        RecordValidator.validate_schema(value, nested_schema.schema),
        key,
    )


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
            errors.extend(_validate_nested_field(key, value, nested_schema))
        return errors

    def _custom_rule(record: Mapping[str, Any]) -> list[ValidationIssue]:
        errors: list[ValidationIssue] = []
        for validator in normalized.custom_validators:
            errors.extend(_coerce_issue(error) for error in validator(record))
        return errors

    return [_nested_rule, _custom_rule]
