from pathlib import Path
from typing import Any

from scrapers.base.complete_extractor_base import CompleteExtractorBase
from scrapers.base.options import ScraperOptions
from scrapers.grands_prix.list_scraper import GrandsPrixListScraper
from scrapers.grands_prix.single_scraper import F1SingleGrandPrixScraper


class F1CompleteGrandPrixDataExtractor(CompleteExtractorBase):
    """
    Pobiera listę Grand Prix, a następnie zaciąga tabelę "By year"
    z każdego artykułu na Wikipedii, rozszerzając rekordy listy.

    Jeżeli artykuł nie wygląda na Grand Prix, pole `by_year` będzie None.
    """

    url = GrandsPrixListScraper.CONFIG.url

    def build_list_scraper(self, options: ScraperOptions) -> GrandsPrixListScraper:
        return GrandsPrixListScraper(options=self.list_scraper_options(options))

    def build_single_scraper(self, options: ScraperOptions) -> F1SingleGrandPrixScraper:
        return F1SingleGrandPrixScraper(options=self.single_scraper_options(options))

    def extract_detail_url(self, record: dict[str, Any]) -> str | None:
        race_title = record.get("race_title")
        if isinstance(race_title, dict):
            return race_title.get("url")
        return None

    def assemble_record(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        full_record = dict(record)
        by_year = details.get("by_year") if details else None
        full_record["by_year"] = by_year
        return full_record


if __name__ == "__main__":
    from scrapers.base.cli_entrypoint import run_cli_entrypoint
    from scrapers.base.helpers.runner import run_and_export
    from scrapers.base.run_config import RunConfig

    run_cli_entrypoint(
        target=lambda *, run_config: run_and_export(
            F1CompleteGrandPrixDataExtractor,
            "grands_prix/f1_grands_prix_extended.json",
            run_config=run_config,
        ),
        base_config=RunConfig(output_dir=Path("../../data/wiki")),
    )
