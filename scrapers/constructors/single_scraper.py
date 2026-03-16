from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.infobox.html_parser import InfoboxHtmlParser
from scrapers.base.options import ScraperOptions
from scrapers.base.sections import SectionAdapter
from scrapers.base.sections import SectionAdapterEntry
from scrapers.constructors.sections import ConstructorChampionshipResultsSectionParser
from scrapers.constructors.sections import ConstructorCompleteF1ResultsSectionParser
from scrapers.constructors.sections import ConstructorHistorySectionParser
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser
from scrapers.wiki.scraper import WikiScraper


class SingleConstructorScraper(SectionAdapter, WikiScraper):
    """
    Scraper pojedynczego konstruktora - pobiera wszystkie infoboksy
    oraz wszystkie tabele z artykułu Wikipedii.
    """

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        options = init_scraper_options(options, include_urls=True)
        policy = self.get_http_policy(options)
        options.with_fetcher(policy=policy)
        super().__init__(options=options)
        self.url: str = ""
        self.article_tables_parser = ArticleTablesParser()

    def fetch_by_url(self, url: str) -> list[dict[str, Any]]:
        self.url = url
        return super().fetch()

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        section_results = self.parse_sections(
            soup=soup,
            domain="constructors",
            entries=[
                SectionAdapterEntry(
                    section_id="History",
                    aliases=(),
                    parser=ConstructorHistorySectionParser(),
                ),
                SectionAdapterEntry(
                    section_id="Championship_results",
                    aliases=("Formula_One/World_Championship_results",),
                    parser=ConstructorChampionshipResultsSectionParser(),
                ),
                SectionAdapterEntry(
                    section_id="Complete_Formula_One_results",
                    aliases=("Complete_World_Championship_results",),
                    parser=ConstructorCompleteF1ResultsSectionParser(),
                ),
            ],
        )
        return [
            {
                "url": self.url,
                "infoboxes": self._scrape_infoboxes(soup),
                "tables": self._scrape_tables(soup),
                "sections": [result.__dict__ for result in section_results],
            },
        ]

    def _scrape_infoboxes(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        parser = InfoboxHtmlParser()
        return [parser.parse_element(table) for table in self.find_infoboxes(soup)]

    def _scrape_tables(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self.article_tables_parser.parse(soup)
