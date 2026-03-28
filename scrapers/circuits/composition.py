from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from scrapers.base.sections.factory import ValidatingSectionServiceFactory
from scrapers.circuits.services.domain_record import DomainRecordService
from scrapers.circuits.infobox.service import CircuitInfoboxExtractionService
from scrapers.circuits.sections.service import CircuitSectionExtractionService

if TYPE_CHECKING:
    from scrapers.base.infobox.service import InfoboxExtractionService
    from scrapers.base.options import ScraperOptions
    from scrapers.base.sections.adapter import SectionAdapter
    from scrapers.base.sections.interface import SectionServiceFactory


class CircuitSectionServiceFactory(
    ValidatingSectionServiceFactory[CircuitSectionExtractionService],
):
    def create(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions | None = None,
        url: str | None = None,
    ) -> CircuitSectionExtractionService:
        self._validate_dependencies(
            adapter=adapter,
            options=options,
            url=url,
            require_options=True,
            require_url=True,
        )
        return CircuitSectionExtractionService(
            adapter=adapter,
            options=options,
            url=url,
        )


@dataclass(frozen=True, slots=True)
class CircuitScraperDependencies:
    infobox_service: InfoboxExtractionService
    sections_service_factory: SectionServiceFactory[CircuitSectionExtractionService]
    domain_record_service: DomainRecordService


@dataclass(frozen=True, slots=True)
class CircuitScraperCompositionFactory:
    """Factory budująca komplet zależności dla F1SingleCircuitScraper."""

    test_mode: bool = False
    infobox_service: InfoboxExtractionService | None = None
    sections_service_factory: (
        SectionServiceFactory[CircuitSectionExtractionService] | None
    ) = None
    domain_record_service: DomainRecordService | None = None

    @classmethod
    def for_tests(
        cls,
        *,
        infobox_service: InfoboxExtractionService | None = None,
        sections_service_factory: (
            SectionServiceFactory[CircuitSectionExtractionService] | None
        ) = None,
        domain_record_service: DomainRecordService | None = None,
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
            infobox_service = CircuitInfoboxExtractionService(options=options)

        sections_service_factory = self.sections_service_factory
        if sections_service_factory is None:
            sections_service_factory = CircuitSectionServiceFactory()

        domain_record_service = self.domain_record_service
        if domain_record_service is None:
            domain_record_service = DomainRecordService()

        return CircuitScraperDependencies(
            infobox_service=infobox_service,
            sections_service_factory=sections_service_factory,
            domain_record_service=domain_record_service,
        )
