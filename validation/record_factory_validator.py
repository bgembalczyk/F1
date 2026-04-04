"""Adapters for unifying record-factory validation contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol

if TYPE_CHECKING:
    from collections.abc import Callable

    from validation.issue import ValidationIssue

ExportRecord = dict[str, Any]


class RecordFactoryValidatorProtocol(Protocol):
    """Unified contract used by ``RecordValidator`` for factory-level validation."""

    def __call__(self, record: ExportRecord) -> list[ValidationIssue | str]: ...


@dataclass(frozen=True, slots=True)
class ModelValidateRecordFactoryValidatorAdapter:
    """Adapter for factories exposing ``model_validate(record)``."""

    validator: Callable[[ExportRecord], Any]

    def __call__(self, record: ExportRecord) -> list[ValidationIssue | str]:
        self.validator(record)
        return []


@dataclass(frozen=True, slots=True)
class ValidateRecordFactoryValidatorAdapter:
    """Adapter for factories exposing ``validate_record(record)``."""

    validator: Callable[[ExportRecord], list[ValidationIssue | str] | None]

    def __call__(self, record: ExportRecord) -> list[ValidationIssue | str]:
        return list(self.validator(record) or [])


@dataclass(frozen=True, slots=True)
class ValidateMethodRecordFactoryValidatorAdapter:
    """Adapter for instance factories exposing ``validate()`` without arguments."""

    validator: Callable[[], Any]

    def __call__(self, _record: ExportRecord) -> list[ValidationIssue | str]:
        self.validator()
        return []


def adapt_record_factory_validator(
    record_factory: object | None,
) -> RecordFactoryValidatorProtocol | None:
    """Build adapter for legacy record-factory validation variants."""
    if record_factory is None:
        return None

    model_validate = getattr(record_factory, "model_validate", None)
    if callable(model_validate):
        return ModelValidateRecordFactoryValidatorAdapter(validator=model_validate)

    validate_record = getattr(record_factory, "validate_record", None)
    if callable(validate_record):
        return ValidateRecordFactoryValidatorAdapter(validator=validate_record)

    validate = getattr(record_factory, "validate", None)
    if callable(validate) and not isinstance(record_factory, type):
        return ValidateMethodRecordFactoryValidatorAdapter(validator=validate)

    return None
