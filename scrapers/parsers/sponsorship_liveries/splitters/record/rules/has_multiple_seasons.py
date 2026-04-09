from scrapers.parsers.sponsorship_liveries.splitters.record.pipeline_record import PipelineRecord


class HasMultipleSeasonsRule:
    def should_apply(self, record: PipelineRecord) -> bool:
        seasons = record.payload.get("season")
        return isinstance(seasons, list) and len(seasons) > 1
