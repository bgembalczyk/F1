from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.seasons.sections.service import SeasonTextSectionExtractionService

if TYPE_CHECKING:
    from scrapers.base.options import ScraperOptions
    from scrapers.base.sections.adapter import SectionAdapter


class SeasonTextSectionServiceFactory:
    def create(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions,
        url: str,
    ) -> SeasonTextSectionExtractionService:
        _ = options, url
        return SeasonTextSectionExtractionService(adapter=adapter)
