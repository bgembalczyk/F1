from typing import Any

from scrapers.sponsorship_liveries.parsers.splitters.record.pipeline import (
    RecordSplitPipeline,
)
from scrapers.sponsorship_liveries.parsers.splitters.record.strategies import (
    deduplicate,
)
from scrapers.sponsorship_liveries.parsers.splitters.record.strategies import grand_prix
from scrapers.sponsorship_liveries.parsers.splitters.record.strategies import (
    possessive_driver_colour,
)
from scrapers.sponsorship_liveries.parsers.splitters.record.strategies import season


class SponsorshipRecordSplitter:
    """Facade composing record split strategies in deterministic order."""

    def __init__(self, pipeline: RecordSplitPipeline | None = None):
        self._pipeline = pipeline or RecordSplitPipeline(
            [
                possessive_driver_colour.PossessiveDriverColourSplitStrategy(),
                season.SeasonSplitStrategy(),
                grand_prix.GrandPrixSplitStrategy(),
                deduplicate.DeduplicateRecordStrategy(),
            ],
        )

    def split_record_by_season(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        return self._pipeline.apply(record)
