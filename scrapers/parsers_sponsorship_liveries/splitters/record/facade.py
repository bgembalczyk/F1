from typing import Any

from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters import record


class SponsorshipRecordSplitter:
    """Facade composing record split strategies in deterministic order."""

    def __init__(self, pipeline: record.RecordSplitPipeline | None = None):
        self._pipeline = pipeline or record.RecordSplitPipeline(
            [
                record.PossessiveDriverColourSplitStrategy(),
                record.SeasonSplitStrategy(),
                record.GrandPrixSplitStrategy(),
                record.DeduplicateRecordStrategy(),
            ],
        )

    def split_record_by_season(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        domain_record = record.PipelineRecord.from_input(record)
        return [dict(item.payload) for item in self._pipeline.apply(domain_record)]


__all__ = ["SponsorshipRecordSplitter"]
