from dataclasses import dataclass

from scrapers.infobox_orchestrator_abc import InfoboxOrchestratorABC
from scrapers.services.section.extraction.circuits import CircuitSectionExtractionService
from scrapers.services.section.factories.section_service_factory import SectionServiceFactoryABC
from scrapers.services.domain_record.circuit_pipeline_service import CircuitDomainRecordService


@dataclass(frozen=True, slots=True)
class CircuitScraperDependencies:
    infobox_service: InfoboxOrchestratorABC
    sections_service_factory: SectionServiceFactoryABC[CircuitSectionExtractionService]
    domain_record_service: CircuitDomainRecordService

