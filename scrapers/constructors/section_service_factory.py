from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.constructors.sections.service import ConstructorSectionExtractionService

if TYPE_CHECKING:
    from scrapers.base.options import ScraperOptions
    from scrapers.base.sections.adapter import SectionAdapter


class ConstructorSectionServiceFactory:
    def create(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions,
        url: str,
    ) -> ConstructorSectionExtractionService:
        _ = options, url
        return ConstructorSectionExtractionService(adapter=adapter)
