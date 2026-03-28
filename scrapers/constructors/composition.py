from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from scrapers.base.sections.factory import ValidatingSectionServiceFactory
from scrapers.constructors.domain_record_service import DomainRecordService
from scrapers.constructors.infobox.service import ConstructorInfoboxExtractionService
from scrapers.constructors.sections.service import ConstructorSectionExtractionService

if TYPE_CHECKING:
    from scrapers.base.infobox.service import InfoboxExtractionService
    from scrapers.base.options import ScraperOptions
    from scrapers.base.sections.adapter import SectionAdapter
    from scrapers.base.sections.interface import SectionServiceFactory


class ConstructorSectionServiceFactory(
    ValidatingSectionServiceFactory[ConstructorSectionExtractionService],
):
    def create(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions | None = None,
        url: str | None = None,
    ) -> ConstructorSectionExtractionService:
        self._validate_dependencies(
            adapter=adapter,
            options=options,
            url=url,
            require_options=True,
            require_url=True,
        )
        return ConstructorSectionExtractionService(
            adapter=adapter,
            options=options,
            url=url,
        )


@dataclass(frozen=True, slots=True)
class ConstructorScraperDependencies:
    infobox_service: InfoboxExtractionService
    sections_service_factory: (
        SectionServiceFactory[ConstructorSectionExtractionService]
    )
    domain_record_service: DomainRecordService


@dataclass(frozen=True, slots=True)
class ConstructorScraperCompositionFactory:
    """Factory budująca komplet zależności dla SingleConstructorScraper."""

    test_mode: bool = False
    infobox_service: InfoboxExtractionService | None = None
    sections_service_factory: (
        SectionServiceFactory[ConstructorSectionExtractionService] | None
    ) = None
    domain_record_service: DomainRecordService | None = None

    @classmethod
    def for_tests(
        cls,
        *,
        infobox_service: InfoboxExtractionService | None = None,
        sections_service_factory: (
            SectionServiceFactory[ConstructorSectionExtractionService] | None
        ) = None,
        domain_record_service: DomainRecordService | None = None,
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
            infobox_service = ConstructorInfoboxExtractionService(options=options)

        sections_service_factory = self.sections_service_factory
        if sections_service_factory is None:
            sections_service_factory = ConstructorSectionServiceFactory()

        domain_record_service = self.domain_record_service
        if domain_record_service is None:
            domain_record_service = DomainRecordService()

        return ConstructorScraperDependencies(
            infobox_service=infobox_service,
            sections_service_factory=sections_service_factory,
            domain_record_service=domain_record_service,
        )
