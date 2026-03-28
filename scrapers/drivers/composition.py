from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from scrapers.base.sections.factory import ValidatingSectionServiceFactory
from scrapers.drivers.services.domain_record import DomainRecordService
from scrapers.drivers.infobox.service import DriverInfoboxExtractionService
from scrapers.drivers.sections.service import DriverSectionExtractionService

if TYPE_CHECKING:
    from scrapers.base.infobox.service import InfoboxExtractionService
    from scrapers.base.options import ScraperOptions
    from scrapers.base.sections.adapter import SectionAdapter
    from scrapers.base.sections.interface import SectionServiceFactory


class DriverSectionServiceFactory(
    ValidatingSectionServiceFactory[DriverSectionExtractionService],
):
    def create(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions | None = None,
        url: str | None = None,
    ) -> DriverSectionExtractionService:
        self._validate_dependencies(
            adapter=adapter,
            options=options,
            url=url,
            require_options=True,
            require_url=True,
        )
        return DriverSectionExtractionService(
            adapter=adapter,
            options=options,
            url=url,
        )


@dataclass(frozen=True, slots=True)
class DriverScraperDependencies:
    infobox_service: InfoboxExtractionService
    sections_service_factory: SectionServiceFactory[DriverSectionExtractionService]
    domain_record_service: DomainRecordService


@dataclass(frozen=True, slots=True)
class DriverScraperCompositionFactory:
    """Factory budująca komplet zależności dla SingleDriverScraper."""

    test_mode: bool = False
    infobox_service: InfoboxExtractionService | None = None
    sections_service_factory: (
        SectionServiceFactory[DriverSectionExtractionService] | None
    ) = None
    domain_record_service: DomainRecordService | None = None

    @classmethod
    def for_tests(
        cls,
        *,
        infobox_service: InfoboxExtractionService | None = None,
        sections_service_factory: (
            SectionServiceFactory[DriverSectionExtractionService] | None
        ) = None,
        domain_record_service: DomainRecordService | None = None,
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
            infobox_service = DriverInfoboxExtractionService(options=options)

        sections_service_factory = self.sections_service_factory
        if sections_service_factory is None:
            sections_service_factory = DriverSectionServiceFactory()

        domain_record_service = self.domain_record_service
        if domain_record_service is None:
            domain_record_service = DomainRecordService()

        return DriverScraperDependencies(
            infobox_service=infobox_service,
            sections_service_factory=sections_service_factory,
            domain_record_service=domain_record_service,
        )
