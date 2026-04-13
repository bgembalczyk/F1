from __future__ import annotations

from dataclasses import dataclass

from scrapers.circuit_scraper_dependencies import CircuitScraperDependencies
from scrapers.infobox_orchestrator_abc import InfoboxOrchestratorABC
from scrapers.options import ScraperOptions
from scrapers.orchestration.circuit_orchestrator import CircuitInfoboxOrchestrator
from scrapers.services.section.extraction.circuits import (
    CircuitSectionExtractionService,
)
from scrapers.services.section.factories.configurable import (
    ConfigurableSectionServiceFactory,
)
from scrapers.services.domain_record.circuit_pipeline_service import CircuitDomainRecordService
from scrapers.services.section.factories.section_service_factory import (
    SectionServiceFactoryABC,
)



@dataclass(frozen=True, slots=True)
class CircuitScraperCompositionFactory:
    """Factory budująca komplet zależności dla F1SingleCircuitScraper."""

    test_mode: bool = False
    infobox_service: InfoboxOrchestratorABC | None = None
    sections_service_factory: (
        SectionServiceFactoryABC[CircuitSectionExtractionService] | None
    ) = None
    domain_record_service: CircuitDomainRecordService | None = None

    @classmethod
    def for_tests(
        cls,
        *,
        infobox_service: InfoboxOrchestratorABC | None = None,
        sections_service_factory: (
            SectionServiceFactoryABC[CircuitSectionExtractionService] | None
        ) = None,
        domain_record_service: CircuitDomainRecordService | None = None,
    ) -> CircuitScraperCompositionFactory:
        return cls(
            test_mode=True,
            infobox_service=infobox_service,
            sections_service_factory=sections_service_factory,
            domain_record_service=domain_record_service,
        )

    def build(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> CircuitScraperDependencies:
        infobox_service = self.infobox_service
        if infobox_service is None:
            infobox_service = CircuitInfoboxOrchestrator(options=options)

        sections_service_factory = self.sections_service_factory
        if sections_service_factory is None:
            sections_service_factory = ConfigurableSectionServiceFactory(
                service_cls=CircuitSectionExtractionService,
                require_options=True,
                require_url=True,
            )

        domain_record_service = self.domain_record_service
        if domain_record_service is None:
            domain_record_service = CircuitDomainRecordService()

        return CircuitScraperDependencies(
            infobox_service=infobox_service,
            sections_service_factory=sections_service_factory,
            domain_record_service=domain_record_service,
        )
