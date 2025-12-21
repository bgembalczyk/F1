from __future__ import annotations

from typing import Any, Dict, Optional

import requests
from bs4 import BeautifulSoup

from http_client.interfaces import HttpClientProtocol
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.helpers.circuits.circuit_normalization import (
    normalize_circuit_record,
)
from scrapers.base.records import ExportRecord, NormalizedRecord, RawRecord
from scrapers.base.registry import register_scraper
from scrapers.base.scraper import F1Scraper
from scrapers.base.run import run_and_export
from scrapers.circuits.list_scraper import F1CircuitsListScraper
from scrapers.circuits.single_scraper import F1SingleCircuitScraper


@register_scraper(
    "circuits_complete",
    "circuits/f1_circuits_extended.json",
    "circuits/f1_circuits_extended.csv",
)
class F1CompleteCircuitScraper(F1Scraper):
    """
    Pobiera listę torów, a następnie zaciąga szczegóły każdego toru (infobox + tabele),
    po czym normalizuje rekord do docelowej struktury.

    Dla torów, których artykuł nie ma "circuit/racetrack"-podobnych kategorii,
    pole `url` będzie miało wartość None, a `layouts` / `history` / `location`
    mogą być puste.
    """

    url = F1CircuitsListScraper.url

    def __init__(
        self,
        *,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional[HttpClientProtocol] = None,
        fetcher: HtmlFetcher | None = None,
    ) -> None:
        if fetcher is None:
            fetcher = HtmlFetcher(
                session=session,
                headers=headers,
                http_client=http_client,
            )
        super().__init__(
            include_urls=True,
            fetcher=fetcher,
        )
        self.list_scraper = F1CircuitsListScraper(
            include_urls=True,
            fetcher=self.fetcher,
        )
        self.single_scraper = F1SingleCircuitScraper(
            fetcher=self.fetcher,
        )

    def fetch(self) -> list[ExportRecord]:
        circuits = self.list_scraper.fetch()
        complete: list[RawRecord] = []

        for circuit in circuits:
            circuit_url: Optional[str] = None
            circuit_data = circuit.get("circuit")
            if isinstance(circuit_data, dict):
                circuit_url = circuit_data.get("url")

            details: Optional[Dict[str, Any]] = None
            if circuit_url:
                details = self.single_scraper.fetch(circuit_url)

            full_record = dict(circuit)
            full_record["details"] = details

            complete.append(full_record)

        normalized_records = self.normalize_records(complete)
        self._data = self.to_export_records(normalized_records)
        return self._data

    def _parse_soup(self, soup: BeautifulSoup) -> list[RawRecord]:
        """Metoda wymagana przez bazę – nie używana w tym scraperze."""
        raise NotImplementedError("Use fetch() bezpośrednio dla pełnego scrapingu")

    def normalize_records(
        self, records: list[RawRecord]
    ) -> list[NormalizedRecord]:
        return [normalize_circuit_record(record) for record in records]


if __name__ == "__main__":
    run_and_export(
        F1CompleteCircuitScraper,
        "../../data/wiki/circuits/f1_circuits_extended.json",
        # csv_path pomijamy – jest opcjonalny
    )
