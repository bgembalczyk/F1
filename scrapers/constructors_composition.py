from __future__ import annotations

from dataclasses import dataclass

from scrapers.infobox.extraction.service import ConstructorInfoboxOrchestrator
from scrapers.infobox_orchestrator_abc import InfoboxOrchestratorABC
from scrapers.options import ScraperOptions
from scrapers.services.section.extraction.constructor import (
    ConstructorSectionExtractionService,
)
from scrapers.services.section.factories.configurable import (
    ConfigurableSectionServiceFactory,
)
from scrapers.services.domain_record.constructor_pipeline_service import ConstructorDomainRecordService
from scrapers.services.section.factories.section_service_factory import (
    SectionServiceFactoryABC,
)


@dataclass(frozen=True, slots=True)
class ConstructorScraperDependencies:
    infobox_service: InfoboxOrchestratorABC
    sections_service_factory: SectionServiceFactoryABC[ConstructorSectionExtractionService]
    domain_record_service: ConstructorDomainRecordService


@dataclass(frozen=True, slots=True)
class ConstructorScraperCompositionFactory:
    """Factory budująca komplet zależności dla SingleConstructorScraper."""

    test_mode: bool = False
    infobox_service: InfoboxOrchestratorABC | None = None
    sections_service_factory: (
        SectionServiceFactoryABC[ConstructorSectionExtractionService] | None
    ) = None
    domain_record_service: ConstructorDomainRecordService | None = None

    @classmethod
    def for_tests(
        cls,
        *,
        infobox_service: InfoboxOrchestratorABC | None = None,
        sections_service_factory: (
            SectionServiceFactoryABC[ConstructorSectionExtractionService] | None
        ) = None,
        domain_record_service: ConstructorDomainRecordService | None = None,
    ) -> ConstructorScraperCompositionFactory:
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
    ) -> ConstructorScraperDependencies:
        infobox_service = self.infobox_service
        if infobox_service is None:
            infobox_service = ConstructorInfoboxOrchestrator(options=options)

        sections_service_factory = self.sections_service_factory
        if sections_service_factory is None:
            sections_service_factory = ConfigurableSectionServiceFactory(
                service_cls=ConstructorSectionExtractionService,
                require_options=True,
                require_url=True,
            )

        domain_record_service = self.domain_record_service
        if domain_record_service is None:
            domain_record_service = ConstructorDomainRecordService()

        return ConstructorScraperDependencies(
            infobox_service=infobox_service,
            sections_service_factory=sections_service_factory,
            domain_record_service=domain_record_service,
        )


__all__ = ["ConstructorScraperCompositionFactory", "ConstructorScraperDependencies"]
