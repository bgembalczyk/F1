from abc import ABC
from abc import abstractmethod

from scrapers.parsers.liveries.sponsorship.splitters.record.pipeline_record import PipelineRecord


class SplitRule(ABC):
    @abstractmethod
    def should_apply(self, record: PipelineRecord) -> bool:
        """Return True when a strategy branch should run for this record."""
