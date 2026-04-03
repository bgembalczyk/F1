"""Composable validation rules shared across record validators."""

from __future__ import annotations

from collections.abc import Mapping
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any
from typing import Protocol
from typing import runtime_checkable

from validation.issue import ValidationIssue

RecordLike = Mapping[str, Any]


@runtime_checkable
class ValidationRuleProtocol(Protocol):
    """Contract for composable validation rules used by validators."""

    rule_name: str
    rule_params: Mapping[str, Any]

    def __call__(self, record: RecordLike) -> Sequence[ValidationIssue | str]: ...

    def validate(self, record: RecordLike) -> Sequence[ValidationIssue | str]: ...


ValidationRule = ValidationRuleProtocol


@dataclass(frozen=True)
class ValueRange:
    """Inclusive value range used by numeric validation rules."""

    min_value: int | float | None = None
    max_value: int | float | None = None


@dataclass(frozen=True)
class RequiredFieldRule:
    field: str
    rule_name: str = "required_field"

    @property
    def rule_params(self) -> Mapping[str, Any]:
        return {"field": self.field}

    def validate(self, record: RecordLike) -> list[ValidationIssue]:
        if self.field in record:
            return []
        return [ValidationIssue.missing(self.field)]

    def __call__(self, record: RecordLike) -> list[ValidationIssue]:
        return self.validate(record)


@dataclass(frozen=True)
class TypeRule:
    field: str
    expected_types: type | tuple[type, ...]
    allow_none: bool = False
    rule_name: str = "type"

    @property
    def rule_params(self) -> Mapping[str, Any]:
        expected = (
            self.expected_types
            if isinstance(self.expected_types, tuple)
            else (self.expected_types,)
        )
        return {
            "field": self.field,
            "expected_types": tuple(
                expected_type.__name__ for expected_type in expected
            ),
            "allow_none": self.allow_none,
        }

    def validate(self, record: RecordLike) -> list[ValidationIssue]:
        if self.field not in record:
            return []
        value = record[self.field]
        if value is None:
            return [] if self.allow_none else [ValidationIssue.null(self.field)]
        if isinstance(value, self.expected_types):
            return []
        expected = (
            self.expected_types
            if isinstance(self.expected_types, tuple)
            else (self.expected_types,)
        )
        expected_names = ", ".join(value_type.__name__ for value_type in expected)
        return [
            ValidationIssue.type_error(
                self.field,
                expected=expected_names,
                actual=type(value).__name__,
            ),
        ]

    def __call__(self, record: RecordLike) -> list[ValidationIssue]:
        return self.validate(record)


@dataclass(frozen=True)
class RangeRule:
    field: str
    value_range: ValueRange
    rule_name: str = "range"

    @property
    def rule_params(self) -> Mapping[str, Any]:
        return {
            "field": self.field,
            "min_value": self.value_range.min_value,
            "max_value": self.value_range.max_value,
        }

    def validate(self, record: RecordLike) -> list[ValidationIssue]:
        if self.field not in record:
            return []
        value = record[self.field]
        if value is None:
            return []
        if not isinstance(value, int | float):
            return []
        if (
            self.value_range.min_value is not None
            and value < self.value_range.min_value
        ):
            return [
                ValidationIssue.custom(
                    f"Value for {self.field} must be >= {self.value_range.min_value}",
                    code="range",
                    field=self.field,
                ),
            ]
        if (
            self.value_range.max_value is not None
            and value > self.value_range.max_value
        ):
            return [
                ValidationIssue.custom(
                    f"Value for {self.field} must be <= {self.value_range.max_value}",
                    code="range",
                    field=self.field,
                ),
            ]
        return []

    def __call__(self, record: RecordLike) -> list[ValidationIssue]:
        return self.validate(record)


def required_field_rule(field: str) -> ValidationRule:
    return RequiredFieldRule(field=field)


def type_rule(
    field: str,
    expected_types: type | tuple[type, ...],
    *,
    allow_none: bool = False,
) -> ValidationRule:
    return TypeRule(field=field, expected_types=expected_types, allow_none=allow_none)


def range_rule(field: str, value_range: ValueRange) -> ValidationRule:
    return RangeRule(field=field, value_range=value_range)


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
