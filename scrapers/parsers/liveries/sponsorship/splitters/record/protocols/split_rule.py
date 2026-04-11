from typing import Protocol

from scrapers.parsers.liveries.sponsorship.splitters.record.pipeline_record import (
    PipelineRecord,
)


class SplitRule(Protocol):
    def should_apply(self, record: PipelineRecord) -> bool:
        """Return True when a strategy branch should run for this record."""
