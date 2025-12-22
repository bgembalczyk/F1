from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from scrapers.base.helpers.circuits.circuit_normalization import (
    normalize_circuit_record,
)
from scrapers.base.options import ScraperOptions
from scrapers.base.registry import register_scraper
from scrapers.base.run import RunConfig, run_and_export
from scrapers.base.scraper import F1Scraper
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.circuits.circuits_list import CircuitsListScraper
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
    pole `details` będzie miało wartość None, a `layouts` / `history` / `location`
    mogą być puste.
    """

    url = CircuitsListScraper.CONFIG.url

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        options = options or ScraperOptions()

        # Ten scraper zawsze potrzebuje URL-i (bo potem dociąga szczegóły)
        options.include_urls = True

        # Zapewniamy adapter źródła (spójnie z resztą repo)
        html_adapter = options.with_source_adapter()
        policy = options.to_http_policy()

        super().__init__(options=options)

        # Pod-scrapery współdzielą ten sam adapter (cache + retry + headers)
        self.list_scraper = CircuitsListScraper(
            options=ScraperOptions(
                include_urls=True,
                policy=policy,
                source_adapter=html_adapter,
            ),
        )
        self.single_scraper = F1SingleCircuitScraper(
            options=ScraperOptions(
                policy=policy,
                source_adapter=html_adapter,
            ),
        )
        self.circuits_adapter = IterableSourceAdapter(self.list_scraper.fetch)

    def fetch(self) -> List[Dict[str, Any]]:
        circuits = self.circuits_adapter.get()
        complete: List[Dict[str, Any]] = []

        for circuit in circuits:
            if not isinstance(circuit, dict):
                raise TypeError(
                    "CircuitsListScraper musi zwracać dict, "
                    f"otrzymano: {type(circuit).__name__}"
                )

            circuit_payload = circuit

            circuit_url: Optional[str] = None
            circuit_data = circuit_payload.get("circuit")
            if isinstance(circuit_data, dict):
                circuit_url = circuit_data.get("url")

            details: Optional[Dict[str, Any]] = None
            if circuit_url:
                details_list = self.single_scraper.fetch(circuit_url)
                details = details_list[0] if details_list else None

            full_record = dict(circuit_payload)
            full_record["details"] = details

            complete.append(normalize_circuit_record(full_record))

        self._data = complete
        return self._data

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Metoda wymagana przez bazę – nie używana w tym scraperze."""
        raise NotImplementedError("Use fetch() bezpośrednio dla pełnego scrapingu")


if __name__ == "__main__":
    run_and_export(
        F1CompleteCircuitScraper,
        "circuits/f1_circuits_extended.json",
        run_config=RunConfig(output_dir=Path("../../data/wiki")),
    )
