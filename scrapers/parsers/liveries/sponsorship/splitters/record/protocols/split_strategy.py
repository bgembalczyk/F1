from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from scrapers.parsers.liveries.sponsorship.splitters.record.pipeline_record import PipelineRecord


class RecordSplitStrategy(ABC):
    @abstractmethod
    def apply(self, record: PipelineRecord) -> list[PipelineRecord]:
        """Split a record into zero, one, or many records."""
