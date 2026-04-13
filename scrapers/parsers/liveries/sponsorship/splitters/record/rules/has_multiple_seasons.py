from scrapers.parsers.liveries.sponsorship.splitters.record.pipeline_record import (
    PipelineRecord,
)
from scrapers.parsers.liveries.sponsorship.splitters.record.protocols.split_rule import (
    SplitRule,
)


class HasMultipleSeasonsRule(SplitRule):
    def should_apply(self, record: PipelineRecord) -> bool:
        seasons = record.payload.get("season")
        return isinstance(seasons, list) and len(seasons) > 1
