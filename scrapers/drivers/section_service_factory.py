from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.drivers.sections.service import DriverSectionExtractionService

if TYPE_CHECKING:
    from scrapers.base.options import ScraperOptions
    from scrapers.base.sections.adapter import SectionAdapter


class DriverSectionServiceFactory:
    def create(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions,
        url: str,
    ) -> DriverSectionExtractionService:
        return DriverSectionExtractionService(
            adapter=adapter,
            options=options,
            url=url,
        )
