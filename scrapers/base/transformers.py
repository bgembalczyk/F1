from abc import ABC, abstractmethod
from typing import List

from scrapers.base.records import ExportRecord


class RecordTransformer(ABC):
    @abstractmethod
    def transform(self, records: List[ExportRecord]) -> List[ExportRecord]:
        raise NotImplementedError
