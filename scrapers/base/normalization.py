from typing import Any, Callable, Sequence

from scrapers.base.helpers.text_normalization import drop_empty_fields
from scrapers.base.helpers.text_normalization import normalize_record_keys
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
            rules.append(normalize_record_keys)
            rules.append(drop_empty_fields)
        if normalization_rules:
            rules.extend(normalization_rules)
        return rules
