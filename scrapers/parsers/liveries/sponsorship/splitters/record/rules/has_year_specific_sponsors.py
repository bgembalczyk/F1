from scrapers.helpers.constants import SPONSOR_KEYS
from scrapers.parsers.liveries.sponsorship.scope.handlers.sponsor import (
    SponsorScopeHandler,
)
from scrapers.parsers.liveries.sponsorship.splitters.record.pipeline_record import (
    PipelineRecord,
)
from scrapers.parsers.liveries.sponsorship.splitters.record.protocols.split_rule import (
    SplitRule,
)


class HasYearSpecificSponsorsRule(SplitRule):
    def should_apply(self, record: PipelineRecord) -> bool:
        return SponsorScopeHandler.record_has_year_specific_sponsors(
            record.payload,
            SPONSOR_KEYS,
        )
