from __future__ import annotations

from dataclasses import dataclass

from scrapers.infobox.extraction.service import DriverInfoboxOrchestrator
from scrapers.options import ScraperOptions
from scrapers.orchestration.base_infobox_orchestrator import BaseInfoboxOrchestrator
from scrapers.services.domain_record.driver_pipeline_service import (
    DriverPipelineService,
)
from scrapers.services.section.extraction.driver import DriverSectionExtractionService
from scrapers.services.section.factories.configurable import (
    ConfigurableSectionServiceFactory,
)
from scrapers.services.section.factories.section_service_factory import (
    SectionServiceFactoryABC,
)


@dataclass(frozen=True, slots=True)
class DriverScraperDependencies:
    infobox_service: BaseInfoboxOrchestrator
    sections_service_factory: SectionServiceFactoryABC[DriverSectionExtractionService]
    domain_record_service: DriverPipelineService


@dataclass(frozen=True, slots=True)
class DriverScraperCompositionFactory:
    """Factory budująca komplet zależności dla SingleDriverScraper."""

    test_mode: bool = False
    infobox_service: BaseInfoboxOrchestrator | None = None
    sections_service_factory: (
        SectionServiceFactoryABC[DriverSectionExtractionService] | None
    ) = None
    domain_record_service: DriverPipelineService | None = None

    @classmethod
    def for_tests(
        cls,
        *,
        infobox_service: BaseInfoboxOrchestrator | None = None,
        sections_service_factory: (
            SectionServiceFactoryABC[DriverSectionExtractionService] | None
        ) = None,
        domain_record_service: DriverPipelineService | None = None,
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
            domain_record_service = DriverPipelineService()

        return DriverScraperDependencies(
            infobox_service=infobox_service,
            sections_service_factory=sections_service_factory,
            domain_record_service=domain_record_service,
        )
