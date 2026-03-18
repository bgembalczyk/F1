from typing import Any

from scrapers.sponsorship_liveries.parsers.splitters.record.pipeline import RecordSplitPipeline
from scrapers.sponsorship_liveries.parsers.splitters.record.strategies.deduplicate import DeduplicateRecordStrategy
from scrapers.sponsorship_liveries.parsers.splitters.record.strategies.grand_prix import GrandPrixSplitStrategy
from scrapers.sponsorship_liveries.parsers.splitters.record.strategies.possessive_driver_colour import \
    PossessiveDriverColourSplitStrategy
from scrapers.sponsorship_liveries.parsers.splitters.record.strategies.season import SeasonSplitStrategy


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
        return self._pipeline.apply(record)
