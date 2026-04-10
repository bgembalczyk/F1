from scrapers.services.domain_record.season_pipeline_service import SeasonDomainRecordInput
from scrapers.services.domain_record.season_pipeline_service import SeasonPipelineService

DomainRecordService = SeasonPipelineService
SeasonDomainRecordService = SeasonPipelineService

__all__ = ["DomainRecordService", "SeasonDomainRecordService", "SeasonDomainRecordInput"]
