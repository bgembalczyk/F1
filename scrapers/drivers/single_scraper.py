from collections.abc import Callable
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.base.single_wiki_article import SingleWikiArticleSectionAdapterBase
from scrapers.drivers.infobox.service import DriverInfoboxExtractionService
from scrapers.drivers.postprocess import DriverSectionContractPostProcessor
from scrapers.drivers.postprocess.assembler import DriverRecordAssembler
from scrapers.drivers.sections.service import DriverSectionExtractionService


class SingleDriverScraper(SingleWikiArticleSectionAdapterBase):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        infobox_service: DriverInfoboxExtractionService | None = None,
        sections_service_factory: (
            Callable[[ScraperOptions, str], DriverSectionExtractionService] | None
        ) = None,
        assembler: DriverRecordAssembler | None = None,
    ) -> None:
        super().__init__(options=options)
        self.debug_dir = self._options.debug_dir
        self._infobox_service = infobox_service or DriverInfoboxExtractionService(
            include_urls=self.include_urls,
            debug_dir=self.debug_dir,
            run_id=getattr(self, "_run_id", None),
        )
        self._sections_service_factory = sections_service_factory or (
            lambda opts, url: DriverSectionExtractionService(
                adapter=self,
                options=opts,
                url=url,
            )
        )
        self._assembler = assembler or DriverRecordAssembler()

    def _build_post_processor(self) -> DriverSectionContractPostProcessor:
        return DriverSectionContractPostProcessor()

    def _build_infobox_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self._scrape_infoboxes(soup)

    def _scrape_infoboxes(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return [self._infobox_service.extract(soup, url=self.url)]

    def _build_sections_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self._sections_service_factory(self._options, self.url).extract(soup)

    def _parse_results_sections(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self._build_sections_payload(soup)

    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: list[dict[str, Any]],
        sections_payload: list[dict[str, Any]],
    ) -> dict[str, Any]:
        _ = soup
        infobox = infobox_payload[0] if infobox_payload else {}
        return self._assembler.assemble(
            url=self.url,
            infobox=infobox,
            career_results=sections_payload,
        )
