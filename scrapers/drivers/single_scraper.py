from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin
from scrapers.base.options import ScraperOptions
from scrapers.base.sections.adapter import SectionAdapter
from scrapers.drivers.infobox.scraper import DriverInfoboxParser
from scrapers.drivers.sections import driver_section_entries
from scrapers.wiki.scraper import WikiScraper
from scrapers.drivers.postprocess import DriverSectionContractPostProcessor


class SingleDriverScraper(SectionAdapter, WikipediaSectionByIdMixin, WikiScraper):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        options = init_scraper_options(options, include_urls=True)
        policy = self.get_http_policy(options)
        options.with_fetcher(policy=policy)
        options.post_processors.append(DriverSectionContractPostProcessor())
        super().__init__(options=options)
        self.url: str = ""
        self._options = options
        self.debug_dir = options.debug_dir

    def fetch_by_url(self, url: str) -> list[dict[str, Any]]:
        self.url = url
        return super().fetch()

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        sections = self.parse_section_dicts(
            soup=soup,
            domain="drivers",
            entries=driver_section_entries(options=self._options, url=self.url),
        )
        return [
            {
                "url": self.url,
                "infobox": self._scrape_infobox(soup),
                "sections": sections,
                "career_results": self._parse_results_sections(sections),
            },
        ]

    def _scrape_infobox(self, soup: BeautifulSoup) -> dict[str, Any]:
        table = self.find_infobox(soup)
        if table is None:
            return {}
        infobox_scraper = DriverInfoboxParser(
            options=ScraperOptions(
                include_urls=self.include_urls,
                debug_dir=self.debug_dir,
            ),
            run_id=getattr(self, "_run_id", None),
            url=self.url,
        )
        records = infobox_scraper.parse(table)
        return records[0] if records else {}

    def _parse_results_sections(self, sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for section in sections:
            records.extend(
                {
                    **record,
                    "section": section["section_label"],
                    "section_id": section["section_id"],
                }
                for record in section["records"]
            )
        return records
