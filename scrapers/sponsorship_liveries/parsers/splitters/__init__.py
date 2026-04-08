from scrapers.sponsorship_liveries.parsers.splitters.broader_scope import (
    BroaderScopeSplitter,
)
from scrapers.sponsorship_liveries.parsers.splitters.depth_aware_colour import (
    DepthAwareColourSplitter,
)
from scrapers.sponsorship_liveries.parsers.splitters.record import (
    DeduplicateRecordStrategy,
)
from scrapers.sponsorship_liveries.parsers.splitters.record import (
    GrandPrixSplitStrategy,
)
from scrapers.sponsorship_liveries.parsers.splitters.record import (
    HasMultipleSeasonsRule,
)
from scrapers.sponsorship_liveries.parsers.splitters.record import (
    HasPossessiveColoursRule,
)
from scrapers.sponsorship_liveries.parsers.splitters.record import (
    HasYearSpecificColoursRule,
)
from scrapers.sponsorship_liveries.parsers.splitters.record import (
    HasYearSpecificSponsorsRule,
)
from scrapers.sponsorship_liveries.parsers.splitters.record import PipelineRecord
from scrapers.sponsorship_liveries.parsers.splitters.record import (
    PossessiveDriverColourSplitStrategy,
)
from scrapers.sponsorship_liveries.parsers.splitters.record import RecordSplitPipeline
from scrapers.sponsorship_liveries.parsers.splitters.record import RecordSplitStrategy
from scrapers.sponsorship_liveries.parsers.splitters.record import SeasonSplitStrategy
from scrapers.sponsorship_liveries.parsers.splitters.record import SplitRule
from scrapers.sponsorship_liveries.parsers.splitters.record import (
    SponsorshipRecordSplitter,
)

__all__ = [
    "BroaderScopeSplitter",
    "DepthAwareColourSplitter",
    "SponsorshipRecordSplitter",
    "RecordSplitPipeline",
    "PipelineRecord",
    "RecordSplitStrategy",
    "SplitRule",
    "HasMultipleSeasonsRule",
    "HasPossessiveColoursRule",
    "HasYearSpecificColoursRule",
    "HasYearSpecificSponsorsRule",
    "GrandPrixSplitStrategy",
    "PossessiveDriverColourSplitStrategy",
    "SeasonSplitStrategy",
    "DeduplicateRecordStrategy",
]
