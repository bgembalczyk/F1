from scrapers.helpers.constants import SPONSOR_KEYS
from scrapers.parsers.sponsorship_liveries.scope.handlers.sponsor import SponsorScopeHandler
from scrapers.parsers.sponsorship_liveries.splitters.record.pipeline_record import PipelineRecord


class HasYearSpecificSponsorsRule:
    def should_apply(self, record: PipelineRecord) -> bool:
        return SponsorScopeHandler.record_has_year_specific_sponsors(
            record.payload,
            SPONSOR_KEYS,
        )
