from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from scrapers.base.scraper import F1Scraper
from scrapers.circuits.list_scraper import F1CircuitsListScraper
from scrapers.circuits.single_scraper import F1SingleCircuitScraper


class F1CompleteCircuitScraper(F1Scraper):
    """
    Pobiera listę torów, a następnie zaciąga szczegóły każdego toru (infobox + tabele).

    Dla torów, których artykuł nie ma "circuit/racetrack"-podobnych kategorii,
    pole `details` będzie miało wartość None.
    """

    url = F1CircuitsListScraper.url

    def __init__(
        self,
        *,
        delay_seconds: float = 1.0,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(include_urls=True, session=session, headers=headers)
        self.delay_seconds = delay_seconds
        self.list_scraper = F1CircuitsListScraper(
            include_urls=True,
            session=self.session,
        )
        self.single_scraper = F1SingleCircuitScraper(
            session=self.session,
            delay_seconds=delay_seconds,
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
            complete.append(full_record)

        self._data = complete
        return self._data

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Metoda wymagana przez bazę – nie używana w tym scraperze."""
        raise NotImplementedError("Use fetch() bezpośrednio dla pełnego scrapingu")


if __name__ == "__main__":
    scraper = F1CompleteCircuitScraper(delay_seconds=1.0)
    data = scraper.fetch()
    print(f"Pobrano {len(data)} rekordów z pełnymi danymi torów.")

    scraper.to_json("../../data/wiki/circuits/f1_circuits_extended.json")
