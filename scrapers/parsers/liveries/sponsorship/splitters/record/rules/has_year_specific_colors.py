from scrapers.helpers.constants import COLOUR_KEYS
from scrapers.parsers.liveries.sponsorship.scope.handlers.colour import (
    ColourScopeHandler,
)
from scrapers.parsers.liveries.sponsorship.splitters.record.pipeline_record import (
    PipelineRecord,
)


class HasYearSpecificColoursRule:
    def should_apply(self, record: PipelineRecord) -> bool:
        return ColourScopeHandler.record_has_year_specific_colours(
            record.payload,
            COLOUR_KEYS,
        )
