"""Helpers that convert ``RecordSchema`` into composable rule lists."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from validation.issue import ValidationIssue
from validation.rules import ValidationRule
from validation.schemas import RecordSchema
from validation.validator_base import RecordValidator


def build_domain_rules(schema: RecordSchema | Mapping[str, Any]) -> list[ValidationRule]:
    normalized = RecordValidator._coerce_schema(schema)

    def _nested_rule(record: Mapping[str, Any]) -> list[ValidationIssue]:
        errors: list[ValidationIssue] = []
        for key, nested_schema in normalized.nested.items():
            if key not in record:
                continue
            value = record[key]
            if value is None:
                continue
            errors.extend(RecordValidator._validate_nested_value(key, value, nested_schema))
        return errors

    def _custom_rule(record: Mapping[str, Any]) -> list[ValidationIssue]:
        errors: list[ValidationIssue] = []
        for validator in normalized.custom_validators:
            errors.extend(RecordValidator._coerce_issue(error) for error in validator(record))
        return errors

    return [_nested_rule, _custom_rule]
