from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from tqdm import tqdm

from scrapers.base.abc import ABCScraper
from scrapers.base.data_extractor import BaseDataExtractor
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.base.helpers.wiki import is_wikipedia_redlink
from scrapers.constructors.former_constructors_list import FormerConstructorsListScraper
from scrapers.constructors.list.current import CurrentConstructorsListScraper
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
        single_scraper_factory: Callable[[ScraperOptions], SingleConstructorScraper]
        | None = None,
        current_list_scraper_factory: (
            Callable[[ScraperOptions], CurrentConstructorsListScraper] | None
        ) = None,
        former_list_scraper_factory: (
            Callable[[ScraperOptions], FormerConstructorsListScraper] | None
        ) = None,
        indianapolis_list_scraper_factory: (
            Callable[[ScraperOptions], IndianapolisOnlyConstructorsListScraper] | None
        ) = None,
        privateer_list_scraper_factory: (
            Callable[[ScraperOptions], PrivateerTeamsListScraper] | None
        ) = None,
    ) -> None:
        options = init_scraper_options(options, include_urls=True)
        policy = self.get_http_policy(options)
        options.with_fetcher(policy=policy)
        super().__init__(options=options)
        self._options = options
        self._single_scraper_factory = single_scraper_factory or SingleConstructorScraper
        self._current_list_scraper_factory = (
            current_list_scraper_factory or CurrentConstructorsListScraper
        )
        self._former_list_scraper_factory = (
            former_list_scraper_factory or FormerConstructorsListScraper
        )
        self._indianapolis_list_scraper_factory = (
            indianapolis_list_scraper_factory
            or IndianapolisOnlyConstructorsListScraper
        )
        self._privateer_list_scraper_factory = (
            privateer_list_scraper_factory or PrivateerTeamsListScraper
        )

    def fetch(self) -> list[dict[str, Any]]:
        single_scraper = self._single_scraper_factory(self._options)
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
            self._current_list_scraper_factory(options=self._options),
            self._former_list_scraper_factory(options=self._options),
            self._indianapolis_list_scraper_factory(options=self._options),
            self._privateer_list_scraper_factory(options=self._options),
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
