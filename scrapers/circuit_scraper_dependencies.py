from dataclasses import dataclass

from scrapers.infobox_orchestrator_protocol import InfoboxOrchestratorProtocol
from scrapers.services.section.extraction.circuits import CircuitSectionExtractionService
from scrapers.services.section.factories.section_service_factory import SectionServiceFactoryABC


@dataclass(frozen=True, slots=True)
class CircuitScraperDependencies:
    infobox_service: InfoboxOrchestratorProtocol
    sections_service_factory: SectionServiceFactoryABC[CircuitSectionExtractionService]
    domain_record_service: CircuitDomainRecordService

