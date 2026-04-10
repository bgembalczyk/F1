from scrapers.services.domain_record.constructor_pipeline_service import ConstructorDomainRecordInput
from scrapers.services.domain_record.constructor_pipeline_service import ConstructorPipelineService

DomainRecordService = ConstructorPipelineService
ConstructorDomainRecordService = ConstructorPipelineService

__all__ = [
    "DomainRecordService",
    "ConstructorDomainRecordService",
    "ConstructorDomainRecordInput",
]
