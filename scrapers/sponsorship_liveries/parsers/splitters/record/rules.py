from scrapers.sponsorship_liveries.helpers.constants import COLOUR_KEYS
from scrapers.sponsorship_liveries.helpers.constants import SPONSOR_KEYS
from scrapers.sponsorship_liveries.parsers.scope_handlers.colour import (
    ColourScopeHandler,
)
from scrapers.sponsorship_liveries.parsers.scope_handlers.sponsor import (
    SponsorScopeHandler,
)
from scrapers.sponsorship_liveries.parsers.splitters.record.pipeline_record import (
    PipelineRecord,
)


class HasPossessiveColoursRule:
    def should_apply(self, record: PipelineRecord) -> bool:
        return any(
            ColourScopeHandler.has_possessive_colour_groups(record.payload.get(key))
            for key in COLOUR_KEYS
        )


class HasMultipleSeasonsRule:
    def should_apply(self, record: PipelineRecord) -> bool:
        seasons = record.payload.get("season")
        return isinstance(seasons, list) and len(seasons) > 1


class HasYearSpecificSponsorsRule:
    def should_apply(self, record: PipelineRecord) -> bool:
        return SponsorScopeHandler.record_has_year_specific_sponsors(
            record.payload,
            SPONSOR_KEYS,
        )


class HasYearSpecificColoursRule:
    def should_apply(self, record: PipelineRecord) -> bool:
        return ColourScopeHandler.record_has_year_specific_colours(
            record.payload,
            COLOUR_KEYS,
        )
