from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin
from scrapers.base.options import ScraperOptions
from scrapers.base.sections.adapter import SectionAdapter
from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.drivers.infobox.scraper import DriverInfoboxParser
from scrapers.drivers.postprocess import DriverSectionContractPostProcessor
from scrapers.drivers.sections import DriverCareerSectionParser
from scrapers.drivers.sections import DriverNonChampionshipSectionParser
from scrapers.drivers.sections import DriverRacingRecordSectionParser
from scrapers.drivers.sections.results import DriverResultsSectionParser
from scrapers.wiki.scraper import WikiScraper


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
        return [
            {
                "url": self.url,
                "infobox": self._scrape_infobox(soup),
                "career_results": self._parse_results_sections(soup),
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

    def _parse_results_sections(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        raw_parser = DriverResultsSectionParser(options=self._options, url=self.url)
        sections = self.parse_sections(
            soup=soup,
            domain="drivers",
            entries=[
                SectionAdapterEntry(
                    section_id="Career_results",
                    aliases=profile_entry_aliases(
                        "drivers",
                        "Career_results",
                        "Karting_record",
                    ),
                    parser=DriverCareerSectionParser(parser=raw_parser),
                ),
                SectionAdapterEntry(
                    section_id="Racing_record",
                    aliases=profile_entry_aliases(
                        "drivers",
                        "Racing_record",
                        "Motorsport_career_results",
                    ),
                    parser=DriverRacingRecordSectionParser(parser=raw_parser),
                ),
                SectionAdapterEntry(
                    section_id="Non-championship",
                    aliases=profile_entry_aliases(
                        "drivers",
                        "Non-championship",
                        "Non-championship_races",
                    ),
                    parser=DriverNonChampionshipSectionParser(parser=raw_parser),
                ),
            ],
        )
        records: list[dict[str, Any]] = []
        for section in sections:
            records.extend(
                {
                    **record,
                    "section": section.section_label,
                    "section_id": section.section_id,
                }
                for record in section.records
            )
        return records
