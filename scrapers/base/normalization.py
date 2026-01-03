from typing import Any, Callable, Sequence

from scrapers.base.helpers.text_normalization import drop_empty_fields
from scrapers.base.helpers.text_normalization import normalize_record_keys
from scrapers.base.logging import get_logger
from scrapers.base.null_policy import normalize_empty
from scrapers.base.records import ExportRecord

NormalizationRule = Callable[[ExportRecord], ExportRecord]


class RecordNormalizer:
    def __init__(
        self,
        *,
        normalize_keys: bool = False,
        normalize_empty_values: bool = False,
        normalization_rules: Sequence[NormalizationRule] | None = None,
    ) -> None:
        self._normalize_empty_values = normalize_empty_values
        self._rules = self._build_normalization_rules(
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )
        self.logger = get_logger(self.__class__.__name__)

    @property
    def has_rules(self) -> bool:
        return bool(self._rules) or self._normalize_empty_values

    def normalize(self, data: Sequence[ExportRecord | Any]) -> list[ExportRecord | Any]:
        if not self._rules and not self._normalize_empty_values:
            return list(data)
        normalized: list[ExportRecord | Any] = []
        normalized_empty_fields = 0
        for item in data:
            if not isinstance(item, dict):
                normalized.append(item)
                continue
            updated, empty_count = self.normalize_record(item)
            normalized_empty_fields += empty_count
            normalized.append(updated)
        if self._normalize_empty_values and normalized_empty_fields:
            self.logger.debug(
                "RecordNormalizer normalized %d empty field(s)",
                normalized_empty_fields,
            )
        return normalized

    def normalize_record(self, record: ExportRecord) -> tuple[ExportRecord, int]:
        updated: ExportRecord = dict(record)
        normalized_empty_fields = 0
        if self._normalize_empty_values:
            updated, normalized_empty_fields = self._normalize_empty_fields(updated)
        for rule in self._rules:
            updated = rule(updated)
        return updated, normalized_empty_fields

    @staticmethod
    def _normalize_empty_fields(record: ExportRecord) -> tuple[ExportRecord, int]:
        normalized: ExportRecord = {}
        normalized_empty_fields = 0
        for key, value in record.items():
            cleaned = normalize_empty(value)
            if cleaned is None and (
                (isinstance(value, str) and value.strip() == "")
                or (isinstance(value, (list, dict)) and not value)
            ):
                normalized_empty_fields += 1
            normalized[key] = cleaned
        return normalized, normalized_empty_fields

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
