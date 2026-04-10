from scrapers.services.domain_record.circuit_pipeline_service import CircuitDomainRecordInput
from scrapers.services.domain_record.circuit_pipeline_service import CircuitPipelineService

DomainRecordService = CircuitPipelineService
CircuitDomainRecordService = CircuitPipelineService

__all__ = ["DomainRecordService", "CircuitDomainRecordService", "CircuitDomainRecordInput"]
