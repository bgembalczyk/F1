from abc import ABC
from abc import abstractmethod
from typing import Any

from scrapers.normalization_utils import EmptyValuePolicy
from scrapers.normalization_utils import normalize_record_values
from validation.validator_base import ExportRecord


class RecordTransformer(ABC):
    def __init__(
        self,
        *,
        empty_value_policy: EmptyValuePolicy = EmptyValuePolicy.NORMALIZE,
    ) -> None:
        self.empty_value_policy = empty_value_policy

    def normalize_record(self, record: ExportRecord | Any) -> ExportRecord | Any:
        if not isinstance(record, dict):
            return record
        normalized, _ = normalize_record_values(
            record,
            policy=self.empty_value_policy,
        )
        return normalized

    @abstractmethod
    def transform(self, records: list[ExportRecord]) -> list[ExportRecord]:
        raise NotImplementedError


__all__ = ["RecordTransformer"]
