from typing import Any

from tqdm import tqdm

from scrapers.base.abc import ABCScraper
from scrapers.base.data_extractor import BaseDataExtractor
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.helpers.wiki import is_wikipedia_redlink
from scrapers.base.options import ScraperOptions
from scrapers.base.output_layout import output_dir_for
from scrapers.constructors.current_constructors_list import (
    CurrentConstructorsListScraper,
)
from scrapers.constructors.former_constructors_list import FormerConstructorsListScraper
from scrapers.constructors.indianapolis_only_constructors_list import (
    IndianapolisOnlyConstructorsListScraper,
)
from scrapers.constructors.privateer_teams_list import PrivateerTeamsListScraper
from scrapers.constructors.single_scraper import SingleConstructorScraper


class CompleteConstructorsDataExtractor(BaseDataExtractor):
    """
    Uruchamia cztery list scrapery konstruktorów, a następnie dla każdego
    elementu pobiera szczegóły (infoboksy + tabele) za pomocą
    SingleConstructorScraper.
    """

    url = CurrentConstructorsListScraper.CONFIG.url

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        options = init_scraper_options(options, include_urls=True)
        policy = self.get_http_policy(options)
        options.with_fetcher(policy=policy)
        super().__init__(options=options)
        self._options = options

    def fetch(self) -> list[dict[str, Any]]:
        single_scraper = SingleConstructorScraper(options=self._options)
        records = self._fetch_all_list_records()

        results: list[dict[str, Any]] = []
        for record in tqdm(
            records,
            desc="CompleteConstructorsDataExtractor",
            unit="constructor",
        ):
            detail_url = self._get_constructor_url(record)
            details: dict[str, Any] | None = None

            if detail_url:
                try:
                    details_list = single_scraper.fetch_by_url(detail_url)
                    details = details_list[0] if details_list else None
                except Exception:
                    self.logger.exception(
                        "Nie udało się pobrać szczegółów konstruktora (url=%s).",
                        detail_url,
                    )

            assembled = dict(record)
            assembled["details"] = details
            results.append(assembled)

        self._data = results
        return self._data

    def _fetch_all_list_records(self) -> list[dict[str, Any]]:
        list_scrapers: list[ABCScraper] = [
            CurrentConstructorsListScraper(options=self._options),
            FormerConstructorsListScraper(options=self._options),
            IndianapolisOnlyConstructorsListScraper(options=self._options),
            PrivateerTeamsListScraper(options=self._options),
        ]

        all_records: list[dict[str, Any]] = []
        for scraper in list_scrapers:
            try:
                records = scraper.fetch()
                all_records.extend(records)
            except Exception:  # noqa: PERF203
                self.logger.exception(
                    "Nie udało się pobrać listy konstruktorów (%s).",
                    scraper.__class__.__name__,
                )
        return all_records

    @staticmethod
    def _get_constructor_url(record: dict[str, Any]) -> str | None:
        # CurrentConstructorsListScraper / FormerConstructorsListScraper:
        # constructor is a LinkRecord dict with "url" key
        constructor = record.get("constructor")
        if isinstance(constructor, dict):
            url = constructor.get("url")
            if isinstance(url, str) and url and not is_wikipedia_redlink(url):
                return url

        # IndianapolisOnlyConstructorsListScraper: "constructor_url" key
        url = record.get("constructor_url")
        if isinstance(url, str) and url and not is_wikipedia_redlink(url):
            return url

        # PrivateerTeamsListScraper: "team_url" key
        url = record.get("team_url")
        if isinstance(url, str) and url and not is_wikipedia_redlink(url):
            return url

        return None


if __name__ == "__main__":
    from scrapers.constructors.helpers.export import export_complete_constructors

    export_complete_constructors(
        output_dir=output_dir_for(category="constructors", layer="normalized"),
        include_urls=True,
    )
