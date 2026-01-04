from abc import ABC, abstractmethod
from typing import Any, List

from scrapers.base.normalization import EmptyValuePolicy, normalize_record_values
from validation.records import ExportRecord


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
    def transform(self, records: List[ExportRecord]) -> List[ExportRecord]:
        raise NotImplementedError
