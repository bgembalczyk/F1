from __future__ import annotations

import re
from typing import Any, Callable, Sequence

from scrapers.base.helpers.prune import prune_empty
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

    def normalize(self, data: Sequence[ExportRecord | Any]) -> list[ExportRecord | Any]:
        if not self._rules:
            return list(data)
        normalized: list[ExportRecord | Any] = []
        for item in data:
            if not isinstance(item, dict):
                normalized.append(item)
                continue
            normalized.append(self.normalize_record(item))
        return normalized

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
    pruned = prune_empty(
        record,
        drop_empty_lists=True,
        drop_none=True,
        drop_empty_dicts=True,
    )
    return {
        key: value
        for key, value in pruned.items()
        if not (isinstance(value, str) and value.strip() == "")
    }


def _to_snake_case(value: str) -> str:
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", value)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned.lower()
