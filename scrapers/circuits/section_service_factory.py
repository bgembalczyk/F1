from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.circuits.sections.service import CircuitSectionExtractionService

if TYPE_CHECKING:
    from scrapers.base.options import ScraperOptions
    from scrapers.base.sections.adapter import SectionAdapter


class CircuitSectionServiceFactory:
    def create(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions,
        url: str,
    ) -> CircuitSectionExtractionService:
        return CircuitSectionExtractionService(
            adapter=adapter,
            include_urls=options.include_urls,
            fetcher=options.fetcher,
            policy=options.policy,
            debug_dir=options.debug_dir,
            url=url,
        )
