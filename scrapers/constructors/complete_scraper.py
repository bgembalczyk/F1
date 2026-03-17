from pathlib import Path
from scrapers.base.complete_extractor_base import CompleteExtractorBase
from scrapers.base.helpers.wiki import is_wikipedia_redlink
from scrapers.base.options import ScraperOptions
from scrapers.base.scraper_protocols import ScraperRecord
from scrapers.base.scraper_protocols import ListScraperProtocol
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

    def build_list_scraper(self, options: ScraperOptions) -> ListScraperProtocol:
        msg = "CompleteConstructorsDataExtractor używa build_list_scrapers()."
        raise NotImplementedError(msg)

    def build_list_scrapers(self, options: ScraperOptions) -> list[ListScraperProtocol]:
        list_options = self.list_scraper_options(options)
        return [
            CurrentConstructorsListScraper(options=list_options),
            FormerConstructorsListScraper(options=list_options),
            IndianapolisOnlyConstructorsListScraper(options=list_options),
            PrivateerTeamsListScraper(options=list_options),
        ]

    def build_single_scraper(self, options: ScraperOptions) -> SingleConstructorScraper:
        return SingleConstructorScraper(options=self.single_scraper_options(options))

    def extract_detail_url(self, record: ScraperRecord) -> str | None:
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
    from scrapers.base.cli_entrypoint import build_cli_main
    from scrapers.base.run_config import RunConfig
    from scrapers.constructors.helpers.export import export_complete_constructors

    build_cli_main(
        target=lambda: export_complete_constructors(
            output_dir=Path("../../data/wiki/constructors/complete_constructors"),
            include_urls=True,
        ),
        base_config=RunConfig(),
        profile="complete_extractor",
    )()
