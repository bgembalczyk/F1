from __future__ import annotations

from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any
from typing import Literal
from typing import Protocol
from typing import runtime_checkable

from validation.issue import ValidationIssue

RecordLike = Mapping[str, Any]
ValidationStatus = Literal["valid", "invalid"]


@dataclass(frozen=True)
class ValidationResult:
    status: ValidationStatus
    violations: tuple[ValidationIssue, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.status == "valid"

    @classmethod
    def from_violations(
        cls,
        violations: Sequence[ValidationIssue],
    ) -> "ValidationResult":
        normalized = tuple(violations)
        status: ValidationStatus = "invalid" if normalized else "valid"
        return cls(status=status, violations=normalized)


@runtime_checkable
class StageValidator(Protocol):
    """Single validator unit used by stage pipelines."""

    name: str

    def validate(self, record: RecordLike) -> Sequence[ValidationIssue]:
        ...


@dataclass(frozen=True)
class FunctionalValidator:
    """Adapter exposing a simple callable as ``StageValidator``."""

    name: str
    handler: Callable[[RecordLike], Sequence[ValidationIssue]]

    def validate(self, record: RecordLike) -> Sequence[ValidationIssue]:
        return self.handler(record)


@dataclass(frozen=True)
class ValidationStage:
    name: str
    validators: tuple[StageValidator, ...]

    def validate(self, record: RecordLike) -> list[ValidationIssue]:
        violations: list[ValidationIssue] = []
        for validator in self.validators:
            violations.extend(validator.validate(record))
        return violations


@dataclass(frozen=True)
class ValidationPipeline:
    stages: tuple[ValidationStage, ...]

    def validate(self, record: RecordLike) -> ValidationResult:
        violations: list[ValidationIssue] = []
        for stage in self.stages:
            violations.extend(stage.validate(record))
        return ValidationResult.from_violations(violations)
