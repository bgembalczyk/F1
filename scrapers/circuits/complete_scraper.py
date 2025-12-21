from __future__ import annotations

from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.helpers.circuits.circuit_normalization import normalize_circuit_record
from scrapers.base.options import ScraperOptions
from scrapers.base.registry import register_scraper
from scrapers.base.run import run_and_export
from scrapers.base.scraper import F1Scraper
from scrapers.circuits.list_scraper import F1CircuitsListScraper
from scrapers.circuits.single_scraper import F1SingleCircuitScraper
from models.mappers.serialization import to_dict

# Optional: jeśli istnieje domenowy serwis, użyj go; inaczej fallback do helpera.
try:  # pragma: no cover
    from models.services.circuit_service import CircuitService  # type: ignore
except Exception:  # pragma: no cover
    CircuitService = None  # type: ignore[assignment]


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
    pole `details` będzie miało wartość None, a `layouts` / `history` / `location`
    mogą być puste.
    """

    url = F1CircuitsListScraper.url

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        if options is None:
            options = ScraperOptions()

        # Ten scraper zawsze potrzebuje URL-i (bo potem dociąga szczegóły)
        options.include_urls = True

        # Zapewniamy fetcher (spójnie z resztą repo)
        if options.fetcher is None:
            options.fetcher = HtmlFetcher(
                session=options.session,
                headers=options.headers,
                http_client=options.http_client,
                timeout=options.timeout,
                retries=options.retries,
                cache=options.cache,
            )

        super().__init__(options=options)

        # Pod-scrapery współdzielą ten sam fetcher (cache + retry + headers)
        self.list_scraper = F1CircuitsListScraper(
            options=ScraperOptions(
                include_urls=True,
                fetcher=self.fetcher,
            ),
        )
        self.single_scraper = F1SingleCircuitScraper(
            options=ScraperOptions(
                fetcher=self.fetcher,
            ),
        )

    def _normalize(self, full_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizacja rekordu:
        - jeśli dostępny CircuitService → delegujemy do domeny
        - inaczej → używamy lokalnej normalizacji (helpers).
        """
        if CircuitService is not None:
            return CircuitService.normalize_record(full_record)
        return normalize_circuit_record(full_record)

    def fetch(self) -> List[Dict[str, Any]]:
        circuits = self.list_scraper.fetch()
        complete: List[Dict[str, Any]] = []

        for circuit in circuits:
            circuit_payload = to_dict(circuit)
            circuit_url: Optional[str] = None
            circuit_data = circuit_payload.get("circuit")
            if isinstance(circuit_data, dict):
                circuit_url = circuit_data.get("url")

            details: Optional[Dict[str, Any]] = None
            if circuit_url:
                details = self.single_scraper.fetch(circuit_url)

            full_record = dict(circuit_payload)
            full_record["details"] = details

            complete.append(self._normalize(full_record))

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
