from dataclasses import dataclass

from scrapers.orchestration.base_infobox_orchestrator import BaseInfoboxOrchestrator
from scrapers.services.domain_record.circuit_pipeline_service import (
    CircuitPipelineService,
)
from scrapers.services.section.extraction.circuits import (
    CircuitSectionExtractionService,
)
from scrapers.services.section.factories.section_service_factory import (
    SectionServiceFactoryABC,
)


@dataclass(frozen=True, slots=True)
class CircuitScraperDependencies:
    infobox_service: BaseInfoboxOrchestrator
    sections_service_factory: SectionServiceFactoryABC[CircuitSectionExtractionService]
    domain_record_service: CircuitPipelineService
