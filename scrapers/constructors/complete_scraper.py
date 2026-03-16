from pathlib import Path
from typing import Any

from scrapers.base.composite_scraper import CompositeDataExtractor
from scrapers.base.composite_scraper import CompositeDataExtractorChildren
from scrapers.base.detail_url_resolver import ConstructorDetailUrlResolver
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.base.source_adapter import MultiIterableSourceAdapter
from scrapers.constructors.current_constructors_list import (
    CurrentConstructorsListScraper,
)
from scrapers.constructors.former_constructors_list import FormerConstructorsListScraper
from scrapers.constructors.indianapolis_only_constructors_list import (
    IndianapolisOnlyConstructorsListScraper,
)
from scrapers.constructors.privateer_teams_list import PrivateerTeamsListScraper
from scrapers.constructors.single_scraper import SingleConstructorScraper


class CompleteConstructorsDataExtractor(CompositeDataExtractor):
    """
    Uruchamia cztery list scrapery konstruktorów, a następnie dla każdego
    elementu pobiera szczegóły (infoboksy + tabele) za pomocą
    SingleConstructorScraper.
    """

    DETAIL_URL_RESOLVER = ConstructorDetailUrlResolver()
    url = CurrentConstructorsListScraper.CONFIG.url

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        options = init_scraper_options(options, include_urls=True)
        policy = self.get_http_policy(options)
        options.with_fetcher(policy=policy)
        self._options = options
        super().__init__(options=options)

    def build_children(self) -> CompositeDataExtractorChildren:
        list_scrapers = [
            CurrentConstructorsListScraper(options=self._options),
            FormerConstructorsListScraper(options=self._options),
            IndianapolisOnlyConstructorsListScraper(options=self._options),
            PrivateerTeamsListScraper(options=self._options),
        ]
        records_adapter = MultiIterableSourceAdapter(
            [self._records_fetcher(scraper) for scraper in list_scrapers],
        )
        return CompositeDataExtractorChildren(
            list_scraper=list_scrapers,
            single_scraper=SingleConstructorScraper(options=self._options),
            records_adapter=records_adapter,
        )

    def assemble_record(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        assembled = dict(record)
        assembled["details"] = details
        return assembled

    def _records_fetcher(self, scraper: Any):
        def _fetch() -> list[dict[str, Any]]:
            try:
                return scraper.fetch()
            except Exception:
                self.logger.exception(
                    "Nie udało się pobrać listy konstruktorów (%s).",
                    scraper.__class__.__name__,
                )
                return []

        return _fetch


if __name__ == "__main__":
    from scrapers.base.cli_entrypoint import run_cli_entrypoint
    from scrapers.base.run_config import RunConfig
    from scrapers.constructors.helpers.export import export_complete_constructors

    run_cli_entrypoint(
        target=lambda: export_complete_constructors(
            output_dir=Path("../../data/wiki/constructors/complete_constructors"),
            include_urls=True,
        ),
        base_config=RunConfig(),
    )
