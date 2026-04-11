from typing import Any

from scrapers.parsers.liveries.sponsorship.splitters.record.pipeline_record import (
    PipelineRecord,
)
from scrapers.parsers.liveries.sponsorship.splitters.record.record_split_pipeline import (
    RecordSplitPipeline,
)
from scrapers.parsers.liveries.sponsorship.splitters.record.strategies.deduplicate import (
    DeduplicateRecordStrategy,
)
from scrapers.parsers.liveries.sponsorship.splitters.record.strategies.grand_prix import (
    GrandPrixSplitStrategy,
)
from scrapers.parsers.liveries.sponsorship.splitters.record.strategies.possessive_driver_colour import (
    PossessiveDriverColourSplitStrategy,
)
from scrapers.parsers.liveries.sponsorship.splitters.record.strategies.season import (
    SeasonSplitStrategy,
)


class SponsorshipRecordSplitter:
    """Facade composing record split strategies in deterministic order."""

    def __init__(self, pipeline: RecordSplitPipeline | None = None):
        self._pipeline = pipeline or RecordSplitPipeline(
            [
                PossessiveDriverColourSplitStrategy(),
                SeasonSplitStrategy(),
                GrandPrixSplitStrategy(),
                DeduplicateRecordStrategy(),
            ],
        )

    def split_record_by_season(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        domain_record = PipelineRecord.from_input(record)
        return [dict(item.payload) for item in self._pipeline.apply(domain_record)]


__all__ = ["SponsorshipRecordSplitter"]
