"""Standalone normalization utilities shared across normalizers.

Extracted from scrapers/base/normalization.py to separate free functions from
the ``RecordNormalizer`` class, following the Single Responsibility Principle.
"""

from collections.abc import Callable
from collections.abc import Mapping
from enum import Enum
from typing import Any
from typing import TypeAlias

from validation.validator_base import ExportRecord

NormalizationRule: TypeAlias = Callable[[ExportRecord], ExportRecord]


class EmptyValuePolicy(Enum):
    KEEP = "keep"
    NORMALIZE = "normalize"

    @classmethod
    def from_flag(
        cls, *, normalize_empty_values: bool,
    ) -> "EmptyValuePolicy":
        return cls.NORMALIZE if normalize_empty_values else cls.KEEP


def normalize_empty(
    value: Any,
    *,
    policy: EmptyValuePolicy = EmptyValuePolicy.NORMALIZE,
) -> Any:
    if policy is EmptyValuePolicy.KEEP:
        return value
    if isinstance(value, str):
        return value if value.strip() else None
    if isinstance(value, list | dict):
        return value or None
    return value


def normalize_record_values(
    record: Mapping[str, Any],
    *,
    policy: EmptyValuePolicy,
) -> tuple[ExportRecord, int]:
    if policy is EmptyValuePolicy.KEEP:
        return dict(record), 0
    normalized: ExportRecord = {}
    normalized_empty_fields = 0
    for key, value in record.items():
        cleaned = normalize_empty(value, policy=policy)
        if cleaned is None and (
            (isinstance(value, str) and value.strip() == "")
            or (isinstance(value, (list, dict)) and not value)
        ):
            normalized_empty_fields += 1
        normalized[key] = cleaned
    return normalized, normalized_empty_fields
