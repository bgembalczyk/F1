from scrapers.sponsorship_liveries.parsers.grand_prix_scope import GrandPrixScopeParser
from scrapers.sponsorship_liveries.parsers.parts import SponsorPartsParser
from scrapers.sponsorship_liveries.parsers.record_text import SponsorshipRecordText
from scrapers.sponsorship_liveries.parsers.scope_accumulators import (
    GrandPrixScopeAccumulator,
)
from scrapers.sponsorship_liveries.parsers.section import SponsorshipSectionParser
from scrapers.sponsorship_liveries.parsers.section import SponsorshipTableParser
from scrapers.sponsorship_liveries.parsers.splitters import BroaderScopeSplitter
from scrapers.sponsorship_liveries.parsers.splitters import DeduplicateRecordStrategy
from scrapers.sponsorship_liveries.parsers.splitters import DepthAwareColourSplitter
from scrapers.sponsorship_liveries.parsers.splitters import GrandPrixSplitStrategy
from scrapers.sponsorship_liveries.parsers.splitters import HasMultipleSeasonsRule
from scrapers.sponsorship_liveries.parsers.splitters import HasPossessiveColoursRule
from scrapers.sponsorship_liveries.parsers.splitters import HasYearSpecificColoursRule
from scrapers.sponsorship_liveries.parsers.splitters import HasYearSpecificSponsorsRule
from scrapers.sponsorship_liveries.parsers.splitters import PipelineRecord
from scrapers.sponsorship_liveries.parsers.splitters import (
    PossessiveDriverColourSplitStrategy,
)
from scrapers.sponsorship_liveries.parsers.splitters import RecordSplitPipeline
from scrapers.sponsorship_liveries.parsers.splitters import RecordSplitStrategy
from scrapers.sponsorship_liveries.parsers.splitters import SeasonSplitStrategy
from scrapers.sponsorship_liveries.parsers.splitters import SplitRule
from scrapers.sponsorship_liveries.parsers.splitters import SponsorshipRecordSplitter
from scrapers.sponsorship_liveries.parsers.team_liveries import (
    TeamLiveriesSectionParser,
)
from scrapers.sponsorship_liveries.parsers.team_liveries import TeamLiveriesTableParser

__all__ = [
    "GrandPrixScopeParser",
    "SponsorPartsParser",
    "SponsorshipRecordText",
    "SponsorshipTableParser",
    "SponsorshipSectionParser",
    "TeamLiveriesSectionParser",
    "TeamLiveriesTableParser",
    "GrandPrixScopeAccumulator",
    "SponsorshipRecordText",
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
