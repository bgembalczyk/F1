from __future__ import annotations

import re
from typing import Any, Callable, Sequence

from scrapers.base.records import ExportRecord

NormalizationRule = Callable[[ExportRecord], ExportRecord]


class RecordNormalizer:
    def __init__(
        self,
        *,
        normalize_keys: bool = False,
        normalization_rules: Sequence[NormalizationRule] | None = None,
    ) -> None:
        self._rules = self._build_normalization_rules(
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )

    @property
    def has_rules(self) -> bool:
        return bool(self._rules)

    def normalize(self, data: list[ExportRecord]) -> list[ExportRecord]:
        if not self._rules:
            return list(data)
        return [self.normalize_record(item) for item in data]

    def normalize_record(self, record: ExportRecord) -> ExportRecord:
        updated: ExportRecord = dict(record)
        for rule in self._rules:
            updated = rule(updated)
        return updated

    @staticmethod
    def _build_normalization_rules(
        *,
        normalize_keys: bool,
        normalization_rules: Sequence[NormalizationRule] | None,
    ) -> list[NormalizationRule]:
        rules: list[NormalizationRule] = []
        if normalize_keys:
            rules.append(_normalize_record_keys)
            rules.append(_drop_empty_fields)
        if normalization_rules:
            rules.extend(normalization_rules)
        return rules


def _normalize_record_keys(record: ExportRecord) -> ExportRecord:
    normalized: ExportRecord = {}
    for key, value in record.items():
        normalized_key = _to_snake_case(str(key))
        if not normalized_key:
            continue
        normalized[normalized_key] = value
    return normalized


def _drop_empty_fields(record: ExportRecord) -> ExportRecord:
    return {key: value for key, value in record.items() if not _is_empty(value)}


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) == 0
    return False


def _to_snake_case(value: str) -> str:
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", value)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned.lower()
