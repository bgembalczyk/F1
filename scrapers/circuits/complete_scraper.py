from pathlib import Path
from typing import Any

from scrapers.base.complete_extractor_base import CompleteExtractorBase
from scrapers.base.options import ScraperOptions
from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.circuits.models.services.circuit_service import CircuitService
from scrapers.circuits.single_scraper import F1SingleCircuitScraper


class F1CompleteCircuitDataExtractor(CompleteExtractorBase):
    """
    Pobiera listę torów, a następnie zaciąga szczegóły każdego toru (infobox + tabele),
    po czym normalizuje rekord do docelowej struktury.

    Dla torów, których artykuł nie ma "circuit/racetrack"-podobnych kategorii,
    pole `details` będzie miało wartość None, a `layouts` / `history` / `location`
    mogą być puste.
    """

    url = CircuitsListScraper.CONFIG.url

    def build_list_scraper(self, options: ScraperOptions) -> CircuitsListScraper:
        return CircuitsListScraper(options=self.list_scraper_options(options))

    def build_single_scraper(self, options: ScraperOptions) -> F1SingleCircuitScraper:
        return F1SingleCircuitScraper(options=self.single_scraper_options(options))

    def extract_detail_url(self, record: dict[str, Any]) -> str | None:
        circuit_data = record.get("circuit")
        if isinstance(circuit_data, dict):
            return circuit_data.get("url")
        return None

    def assemble_record(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return CircuitService.normalize_record(super().assemble_record(record, details))


if __name__ == "__main__":
    from scrapers.base.cli_entrypoint import build_cli_main
    from scrapers.base.run_config import RunConfig
    from scrapers.circuits.helpers.export import export_complete_circuits

    build_cli_main(
        target=lambda: export_complete_circuits(
            output_dir=Path("../../data/wiki/circuits/complete_circuits"),
            include_urls=True,
        ),
        base_config=RunConfig(),
        profile="complete_extractor",
    )()
