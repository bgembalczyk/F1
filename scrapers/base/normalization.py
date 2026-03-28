from collections.abc import Sequence
from typing import Any

from models.contracts.helpers import map_record_to_contract
from scrapers.base.helpers.text_normalization import drop_empty_fields
from scrapers.base.helpers.text_normalization import normalize_record_keys
from scrapers.base.logging import get_logger
from scrapers.base.normalization_utils import EmptyValuePolicy
from scrapers.base.normalization_utils import NormalizationRule
from scrapers.base.normalization_utils import normalize_record_values
from validation.validator_base import ExportRecord


class RecordNormalizer:
    def __init__(
        self,
        *,
        normalize_keys: bool = False,
        normalize_empty_values: bool = False,
        empty_value_policy: EmptyValuePolicy | None = None,
        normalization_rules: Sequence[NormalizationRule] | None = None,
    ) -> None:
        self._empty_value_policy = empty_value_policy or EmptyValuePolicy.from_flag(
            normalize_empty_values=normalize_empty_values,
        )
        self._normalize_empty_values = (
            self._empty_value_policy is EmptyValuePolicy.NORMALIZE
        )
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

    def normalize_record(self, record: ExportRecord) -> tuple[ExportRecord | Any, int]:
        updated: ExportRecord = dict(record)
        normalized_empty_fields = 0
        if self._normalize_empty_values:
            updated, normalized_empty_fields = normalize_record_values(
                updated,
                policy=self._empty_value_policy,
            )
        for rule in self._rules:
            updated = rule(updated)
        mapped = map_record_to_contract(updated)
        return mapped, normalized_empty_fields

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
