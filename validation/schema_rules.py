"""Backward-compatible wrappers over ``RecordSchema`` instance methods."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from validation.issue import ValidationIssue
from validation.schemas import RecordSchema

if TYPE_CHECKING:
    from validation.rules import ValidationRule


def _coerce_schema(schema: RecordSchema | dict[str, Any]) -> RecordSchema:
    return RecordSchema.from_mapping(schema)


def _coerce_issue(error: ValidationIssue | str) -> ValidationIssue:
    if isinstance(error, ValidationIssue):
        return error
    return ValidationIssue.custom(str(error))


def build_domain_rules(
    schema: RecordSchema | dict[str, Any],
) -> list[ValidationRule]:
    return _coerce_schema(schema).to_rules()
