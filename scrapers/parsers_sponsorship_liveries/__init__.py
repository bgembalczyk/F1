from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.grand_prix_scope import GrandPrixScopeParser
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.parts import SponsorPartsParser
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.record_text import SponsorshipRecordText
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.scope_accumulators import (
    GrandPrixScopeAccumulator,
)
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.section import SponsorshipSectionParser
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.section import SponsorshipTableParser
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters import BroaderScopeSplitter
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters import DeduplicateRecordStrategy
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters import DepthAwareColourSplitter
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters import GrandPrixSplitStrategy
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters import HasMultipleSeasonsRule
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters import HasPossessiveColoursRule
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters import HasYearSpecificColoursRule
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters import HasYearSpecificSponsorsRule
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters import PipelineRecord
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters import (
    PossessiveDriverColourSplitStrategy,
)
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters import RecordSplitPipeline
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters import RecordSplitStrategy
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters import SeasonSplitStrategy
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters import SplitRule
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.splitters import SponsorshipRecordSplitter
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.team_liveries import (
    TeamLiveriesSectionParser,
)
from scrapers.sponsorship_liveries.parsers_sponsorship_liveries.team_liveries import TeamLiveriesTableParser

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
