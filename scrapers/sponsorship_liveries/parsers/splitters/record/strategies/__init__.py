from scrapers.sponsorship_liveries.parsers.splitters.record.strategies.deduplicate import (
    DeduplicateRecordStrategy,
)
from scrapers.sponsorship_liveries.parsers.splitters.record.strategies.grand_prix import (
    GrandPrixSplitStrategy,
)
from scrapers.sponsorship_liveries.parsers.splitters.record.strategies.possessive_driver_colour import (
    PossessiveDriverColourSplitStrategy,
)
from scrapers.sponsorship_liveries.parsers.splitters.record.strategies.season import (
    SeasonSplitStrategy,
)

__all__ = [
    "GrandPrixSplitStrategy",
    "PossessiveDriverColourSplitStrategy",
    "SeasonSplitStrategy",
    "DeduplicateRecordStrategy",
]
