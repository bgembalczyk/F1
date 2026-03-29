from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Mapping

from scrapers.sponsorship_liveries.parsers.splitters.record.pipeline_record import (
    PipelineRecord,
)

if TYPE_CHECKING:
    from scrapers.sponsorship_liveries.parsers.splitters.record.protocols import (
        RecordSplitStrategy,
    )


class RecordSplitPipeline:
    def __init__(self, strategies: list[RecordSplitStrategy]):
        self._strategies = strategies

    def apply(
        self,
        record: Mapping[str, Any] | PipelineRecord,
    ) -> list[PipelineRecord]:
        for strategy in self._strategies:
            if hasattr(strategy, "reset"):
                strategy.reset()  # type: ignore[attr-defined]

        records = [PipelineRecord.from_input(record)]
        for strategy in self._strategies:
            next_records: list[PipelineRecord] = []
            for candidate in records:
                next_records.extend(strategy.apply(PipelineRecord.from_input(candidate)))
            records = next_records
        return records
