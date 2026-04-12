from __future__ import annotations

from dataclasses import dataclass

from scrapers.infobox.extraction.service import DriverInfoboxOrchestrator
from scrapers.infobox_orchestrator_protocol import InfoboxOrchestratorProtocol
from scrapers.options import ScraperOptions
from scrapers.services.section.extraction.driver import DriverSectionExtractionService
from scrapers.services.section.factories.configurable import (
    ConfigurableSectionServiceFactory,
)
from scrapers.services.section.factories.section_service_factory import (
    SectionServiceFactory,
)


@dataclass(frozen=True, slots=True)
class DriverScraperDependencies:
    infobox_service: InfoboxOrchestratorProtocol
    sections_service_factory: SectionServiceFactory[DriverSectionExtractionService]
    domain_record_service: DriverDomainRecordService


@dataclass(frozen=True, slots=True)
class DriverScraperCompositionFactory:
    """Factory budująca komplet zależności dla SingleDriverScraper."""

    test_mode: bool = False
    infobox_service: InfoboxOrchestratorProtocol | None = None
    sections_service_factory: (
        SectionServiceFactory[DriverSectionExtractionService] | None
    ) = None
    domain_record_service: DriverDomainRecordService | None = None

    @classmethod
    def for_tests(
        cls,
        *,
        infobox_service: InfoboxOrchestratorProtocol | None = None,
        sections_service_factory: (
            SectionServiceFactory[DriverSectionExtractionService] | None
        ) = None,
        domain_record_service: DriverDomainRecordService | None = None,
    ) -> DriverScraperCompositionFactory:
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
    ) -> DriverScraperDependencies:
        infobox_service = self.infobox_service
        if infobox_service is None:
            infobox_service = DriverInfoboxOrchestrator(options=options)

        sections_service_factory = self.sections_service_factory
        if sections_service_factory is None:
            sections_service_factory = ConfigurableSectionServiceFactory(
                service_cls=DriverSectionExtractionService,
                require_options=True,
                require_url=True,
            )

        domain_record_service = self.domain_record_service
        if domain_record_service is None:
            domain_record_service = DriverDomainRecordService()

        return DriverScraperDependencies(
            infobox_service=infobox_service,
            sections_service_factory=sections_service_factory,
            domain_record_service=domain_record_service,
        )
