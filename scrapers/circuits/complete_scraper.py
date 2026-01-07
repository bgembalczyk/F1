from pathlib import Path
from typing import Any, Dict, Optional

from bs4 import BeautifulSoup

from scrapers.base.composite_scraper import (
    CompositeScraper,
    CompositeScraperChildren,
)
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.circuits.models.services.circuit_service import CircuitService
from scrapers.circuits.single_scraper import F1SingleCircuitScraper


class F1CompleteCircuitScraper(CompositeScraper):
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

        super().__init__(options=options)

    def build_children(self) -> CompositeScraperChildren:
        list_scraper = CircuitsListScraper(
            options=ScraperOptions(
                include_urls=True,
                policy=self.http_policy,
                source_adapter=self.source_adapter,
                debug_dir=self.debug_dir,
            ),
        )
        single_scraper = F1SingleCircuitScraper(
            options=ScraperOptions(
                policy=self.http_policy,
                source_adapter=self.source_adapter,
                debug_dir=self.debug_dir,
            ),
        )
        circuits_adapter = IterableSourceAdapter(list_scraper.fetch)

        return CompositeScraperChildren(
            list_scraper=list_scraper,
            single_scraper=single_scraper,
            records_adapter=circuits_adapter,
        )

    def get_detail_url(self, record: Dict[str, Any]) -> Optional[str]:
        circuit_data = record.get("circuit")
        if isinstance(circuit_data, dict):
            return circuit_data.get("url")
        return None

    def assemble_record(
        self,
        record: Dict[str, Any],
        details: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        full_record = dict(record)
        full_record["details"] = details
        return CircuitService.normalize_record(full_record)

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Metoda wymagana przez bazę – nie używana w tym scraperze."""
        raise NotImplementedError("Use fetch() bezpośrednio dla pełnego scrapingu")


if __name__ == "__main__":
    run_and_export(
        F1CompleteCircuitScraper,
        "circuits/f1_circuits_extended.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            debug_dir=Path("../../data/debug"),
        ),
    )
