from __future__ import annotations

from typing import Protocol

from scrapers.parsers.sponsorship_liveries.splitters.record.pipeline_record import PipelineRecord


class RecordSplitStrategy(Protocol):
    def apply(self, record: PipelineRecord) -> list[PipelineRecord]:
        """Split a record into zero, one, or many records."""




