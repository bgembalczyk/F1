from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from f1_http.interfaces import HttpClientProtocol
from scrapers.base.helpers.circuits.circuit_normalization import normalize_circuit_record
from scrapers.base.scraper import F1Scraper
from scrapers.base.run import run_and_export
from scrapers.circuits.list_scraper import F1CircuitsListScraper
from scrapers.circuits.single_scraper import F1SingleCircuitScraper

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
    ) -> None:
        super().__init__(
            include_urls=True,
            session=session,
            headers=headers,
            http_client=http_client,
        )
        self.list_scraper = F1CircuitsListScraper(
            include_urls=True,
            http_client=self.http_client,
        )
        self.single_scraper = F1SingleCircuitScraper(
            http_client=self.http_client,
        )

    def fetch(self) -> List[Dict[str, Any]]:
        circuits = self.list_scraper.fetch()
        complete: List[Dict[str, Any]] = []

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

            normalized = normalize_circuit_record(full_record)
            complete.append(normalized)

        self._data = complete
        return self._data

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Metoda wymagana przez bazę – nie używana w tym scraperze."""
        raise NotImplementedError("Use fetch() bezpośrednio dla pełnego scrapingu")


if __name__ == "__main__":
    run_and_export(
        F1CompleteCircuitScraper,
        "../../data/wiki/circuits/f1_circuits_extended.json",
        # csv_path pomijamy – jest opcjonalny
    )
