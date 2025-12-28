from __future__ import annotations

from typing import Any, Dict, List

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions, init_scraper_options
from scrapers.base.scraper import F1Scraper
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.circuit_location import LocationColumn
from scrapers.base.table.columns.types.constructor_part import ConstructorPartColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.pipeline import TablePipeline
from scrapers.grands_prix.helpers.article_validation import is_grand_prix_article


class F1SingleGrandPrixScraper(F1Scraper):
    """
    Scraper pojedynczego Grand Prix – pobiera tabelę "By year" z artykułu Wikipedii.

    Jeśli artykuł nie wygląda na Grand Prix (brak navboxa/kategorii),
    zwraca pustą listę.
    """

    _SKIP = object()

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        options = init_scraper_options(options, include_urls=True)
        options.with_fetcher()

        super().__init__(options=options)
        self.policy = options.to_http_policy()
        self.timeout = self.policy.timeout
        self.url: str = ""

    def fetch_html(self, url: str) -> str:
        return self.source_adapter.get(url, timeout=self.timeout)

    def fetch_by_url(self, url: str) -> List[Dict[str, Any]]:
        self.url = url
        return super().fetch()

    def _build_pipeline(self, section_id: str) -> TablePipeline:
        config = ScraperConfig(
            url=self.url,
            section_id=section_id,
            expected_headers=["Year", "Driver", "Constructor", "Report"],
            column_map={
                "Year": "year",
                "Driver": "driver",
                "Constructor": "constructor",
                "Report": "report",
                "Location": "location",
            },
            columns={
                "year": UrlColumn(),
                "driver": DriverListColumn(),
                "constructor": MultiColumn(
                    {
                        "chassis_constructor": ConstructorPartColumn(0),
                        "engine_constructor": ConstructorPartColumn(1),
                    }
                ),
                "report": AutoColumn(),
                "location": LocationColumn(),
            },
        )
        return TablePipeline(
            config=config,
            include_urls=self.include_urls,
            skip_sentinel=self._SKIP,
        )

    def _parse_section_table(
        self,
        soup: BeautifulSoup,
        *,
        section_id: str,
    ) -> List[Dict[str, Any]]:
        pipeline = self._build_pipeline(section_id)
        return pipeline.parse_soup(soup)

    def parse(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        if not is_grand_prix_article(soup):
            return []

        for section_id in [
            "By_year",
            "Winners",
            "By_year:_the_European_Grand_Prix_as_a_standalone_event",
            "Winners_of_the_Caesars_Palace_Grand_Prix",
        ]:
            try:
                return [
                    {
                        "url": self.url,
                        "by_year": self._parse_section_table(
                            soup,
                            section_id=section_id,
                        ),
                    }
                ]
            except RuntimeError:
                continue

        return [
            {
                "url": self.url,
                "by_year": [],
            }
        ]
