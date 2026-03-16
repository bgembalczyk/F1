from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.base.sections.adapter import SectionAdapter
from scrapers.circuits.sections import circuit_section_entries


class CircuitSectionExtractionService:
    def __init__(
        self,
        *,
        adapter: SectionAdapter,
        include_urls: bool,
        fetcher: object,
        policy: object,
        debug_dir: str | None,
        url: str,
    ) -> None:
        self._adapter = adapter
        self._include_urls = include_urls
        self._fetcher = fetcher
        self._policy = policy
        self._debug_dir = debug_dir
        self._url = url

    def extract(self, soup: BeautifulSoup) -> list[dict[str, object]]:
        return self._adapter.parse_section_dicts(
            soup=soup,
            domain="circuits",
            entries=circuit_section_entries(
                options=ScraperOptions(
                    include_urls=self._include_urls,
                    fetcher=self._fetcher,
                    policy=self._policy,
                    debug_dir=self._debug_dir,
                ),
                url=self._url,
            ),
        )
