from __future__ import annotations

from dataclasses import dataclass

from scrapers.circuit_orchestrator import CircuitInfoboxOrchestrator
from scrapers.infobox.extraction.protocol import InfoboxExtractionService
from scrapers.infobox.extraction.infobox_orchestrator_protocol import InfoboxOrchestratorProtocol
from scrapers.infobox.extraction.service import CircuitInfoboxOrchestratorProtocol
from scrapers.options import ScraperOptions
from scrapers.services.section.extraction.circuits import (
    CircuitSectionExtractionService,
)
from scrapers.services.section.factories.configurable import (
    ConfigurableSectionServiceFactory,
)
from scrapers.services.section.factories.section_service_factory import (
    SectionServiceFactory,
)


@dataclass(frozen=True, slots=True)
class CircuitScraperDependencies:
    infobox_service: InfoboxOrchestratorProtocol
    sections_service_factory: SectionServiceFactory[CircuitSectionExtractionService]
    domain_record_service: CircuitDomainRecordService


@dataclass(frozen=True, slots=True)
class CircuitScraperCompositionFactory:
    """Factory budująca komplet zależności dla F1SingleCircuitScraper."""

    test_mode: bool = False
    infobox_service: InfoboxOrchestratorProtocol | None = None
    sections_service_factory: (
        SectionServiceFactory[CircuitSectionExtractionService] | None
    ) = None
    domain_record_service: CircuitDomainRecordService | None = None

    @classmethod
    def for_tests(
        cls,
        *,
        infobox_service: InfoboxOrchestratorProtocol | None = None,
        sections_service_factory: (
            SectionServiceFactory[CircuitSectionExtractionService] | None
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
