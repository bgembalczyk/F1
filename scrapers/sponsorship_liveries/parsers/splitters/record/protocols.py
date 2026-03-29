from __future__ import annotations

from typing import Protocol

from scrapers.sponsorship_liveries.parsers.splitters.record.pipeline_record import (
    PipelineRecord,
)


class RecordSplitStrategy(Protocol):
    def apply(self, record: PipelineRecord) -> list[PipelineRecord]:
        """Split a record into zero, one, or many records."""


class SplitRule(Protocol):
    def should_apply(self, record: PipelineRecord) -> bool:
        """Return True when a strategy branch should run for this record."""
