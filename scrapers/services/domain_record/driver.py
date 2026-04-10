from scrapers.services.domain_record.driver_pipeline_service import DriverDomainRecordInput
from scrapers.services.domain_record.driver_pipeline_service import DriverPipelineService

DomainRecordService = DriverPipelineService
DriverDomainRecordService = DriverPipelineService

__all__ = ["DomainRecordService", "DriverDomainRecordService", "DriverDomainRecordInput"]
