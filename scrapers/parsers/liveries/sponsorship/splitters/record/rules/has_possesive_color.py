from scrapers.helpers.constants import COLOUR_KEYS
from scrapers.parsers.liveries.sponsorship.scope.handlers.colour import (
    ColourScopeHandler,
)
from scrapers.parsers.liveries.sponsorship.splitters.record.pipeline_record import (
    PipelineRecord,
)
from scrapers.parsers.liveries.sponsorship.splitters.record.protocols.split_rule import (
    SplitRule,
)


class HasPossessiveColoursRule(SplitRule):
    def should_apply(self, record: PipelineRecord) -> bool:
        return any(
            ColourScopeHandler.has_possessive_colour_groups(record.payload.get(key))
            for key in COLOUR_KEYS
        )
