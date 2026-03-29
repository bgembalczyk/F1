"""Composable validation rules shared across record validators."""

from __future__ import annotations

from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from validation.issue import ValidationIssue

RecordLike = Mapping[str, Any]
ValidationRule = Callable[[RecordLike], Sequence[ValidationIssue]]
LegacyValidationRule = Callable[[RecordLike], Sequence[ValidationIssue | str]]


@dataclass(frozen=True)
class ValueRange:
    """Inclusive value range used by numeric validation rules."""

    min_value: int | float | None = None
    max_value: int | float | None = None


def adapt_legacy_rule(
    rule: LegacyValidationRule,
) -> ValidationRule:
    """Adapt legacy rules returning ``str`` into ``ValidationIssue`` objects."""

    def _rule(record: RecordLike) -> list[ValidationIssue]:
        return [
            (
                issue
                if isinstance(issue, ValidationIssue)
                else ValidationIssue.custom(str(issue))
            )
            for issue in rule(record)
        ]

    return _rule


def required_field_rule(field: str) -> ValidationRule:
    def _rule(record: RecordLike) -> list[ValidationIssue]:
        if field in record:
            return []
        return [ValidationIssue.missing(field)]

    return _rule


def type_rule(
    field: str,
    expected_types: type | tuple[type, ...],
    *,
    allow_none: bool = False,
) -> ValidationRule:
    def _rule(record: RecordLike) -> list[ValidationIssue]:
        if field not in record:
            return []
        value = record[field]
        if value is None:
            return [] if allow_none else [ValidationIssue.null(field)]
        if isinstance(value, expected_types):
            return []
        expected = (
            expected_types if isinstance(expected_types, tuple) else (expected_types,)
        )
        expected_names = ", ".join(value_type.__name__ for value_type in expected)
        return [
            ValidationIssue.type_error(
                field,
                expected=expected_names,
                actual=type(value).__name__,
            ),
        ]

    return _rule


def range_rule(field: str, value_range: ValueRange) -> ValidationRule:
    def _rule(record: RecordLike) -> list[ValidationIssue]:
        if field not in record:
            return []
        value = record[field]
        if value is None:
            return []
        if not isinstance(value, int | float):
            return []
        if value_range.min_value is not None and value < value_range.min_value:
            return [
                ValidationIssue.custom(
                    f"Value for {field} must be >= {value_range.min_value}",
                    code="range",
                    field=field,
                ),
            ]
        if value_range.max_value is not None and value > value_range.max_value:
            return [
                ValidationIssue.custom(
                    f"Value for {field} must be <= {value_range.max_value}",
                    code="range",
                    field=field,
                ),
            ]
        return []

    return _rule


def build_common_rules(
    *,
    required: Sequence[str] = (),
    types: Mapping[str, type | tuple[type, ...]] | None = None,
    allow_none: Sequence[str] = (),
    ranges: Mapping[str, ValueRange] | None = None,
) -> list[ValidationRule]:
    rules: list[ValidationRule] = [required_field_rule(field) for field in required]
    allow_none_set = set(allow_none)
    for field, expected_types in (types or {}).items():
        rules.append(
            type_rule(field, expected_types, allow_none=field in allow_none_set),
        )
    for field, value_range in (ranges or {}).items():
        rules.append(range_rule(field, value_range))
    return rules
