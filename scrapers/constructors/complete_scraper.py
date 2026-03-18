from typing import Any

from complete_extractor.base import CompleteExtractorBase
from scrapers.base.helpers.wiki import is_wikipedia_redlink
from scrapers.base.options import ScraperOptions
from scrapers.constructors.current_constructors_list import (
    CurrentConstructorsListScraper,
)
from scrapers.constructors.former_constructors_list import FormerConstructorsListScraper
from scrapers.constructors.indianapolis_only_constructors_list import (
    IndianapolisOnlyConstructorsListScraper,
)
from scrapers.constructors.privateer_teams_list import PrivateerTeamsListScraper
from scrapers.constructors.single_scraper import SingleConstructorScraper


class CompleteConstructorsDataExtractor(CompleteExtractorBase):
    """
    Uruchamia cztery list scrapery konstruktorów, a następnie dla każdego
    elementu pobiera szczegóły (infoboksy + tabele) za pomocą
    SingleConstructorScraper.
    """

    url = CurrentConstructorsListScraper.CONFIG.url

    def build_list_scraper(self, _options: ScraperOptions) -> Any:
        msg = "CompleteConstructorsDataExtractor używa build_list_scrapers()."
        raise NotImplementedError(msg)

    def build_list_scrapers(self, options: ScraperOptions) -> list[Any]:
        list_options = self.list_scraper_options(options)
        return [
            CurrentConstructorsListScraper(options=list_options),
            FormerConstructorsListScraper(options=list_options),
            IndianapolisOnlyConstructorsListScraper(options=list_options),
            PrivateerTeamsListScraper(options=list_options),
        ]

    def build_single_scraper(self, options: ScraperOptions) -> SingleConstructorScraper:
        return SingleConstructorScraper(options=self.single_scraper_options(options))

    def extract_detail_url(self, record: dict[str, Any]) -> str | None:
        constructor = record.get("constructor")
        if isinstance(constructor, dict):
            url = constructor.get("url")
            if isinstance(url, str) and url and not is_wikipedia_redlink(url):
                return url

        url = record.get("constructor_url")
        if isinstance(url, str) and url and not is_wikipedia_redlink(url):
            return url

        url = record.get("team_url")
        if isinstance(url, str) and url and not is_wikipedia_redlink(url):
            return url

        return None


if __name__ == "__main__":
    from scrapers.cli import run_current_legacy_wrapper

    run_current_legacy_wrapper()
