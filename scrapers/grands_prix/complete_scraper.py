from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.composite_scraper import CompositeScraper
from scrapers.base.composite_scraper import CompositeScraperChildren
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.grands_prix.list_scraper import GrandsPrixListScraper
from scrapers.grands_prix.single_scraper import F1SingleGrandPrixScraper


class F1CompleteGrandPrixScraper(CompositeScraper):
    """
    Pobiera listę Grand Prix, a następnie zaciąga tabelę "By year"
    z każdego artykułu na Wikipedii, rozszerzając rekordy listy.

    Jeżeli artykuł nie wygląda na Grand Prix, pole `by_year` będzie None.
    """

    url = GrandsPrixListScraper.CONFIG.url

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        options = options or ScraperOptions()
        options.include_urls = True

        super().__init__(options=options)

    def build_children(self) -> CompositeScraperChildren:
        list_scraper = GrandsPrixListScraper(
            options=ScraperOptions(
                include_urls=True,
                policy=self.http_policy,
                source_adapter=self.source_adapter,
            ),
        )
        single_scraper = F1SingleGrandPrixScraper(
            options=ScraperOptions(
                policy=self.http_policy,
                source_adapter=self.source_adapter,
            ),
        )
        grands_prix_adapter = IterableSourceAdapter(list_scraper.fetch)

        return CompositeScraperChildren(
            list_scraper=list_scraper,
            single_scraper=single_scraper,
            records_adapter=grands_prix_adapter,
        )

    def get_detail_url(self, record: dict[str, Any]) -> str | None:
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

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Metoda wymagana przez bazę – nie używana w tym scraperze."""
        raise NotImplementedError("Use fetch() bezpośrednio dla pełnego scrapingu")


if __name__ == "__main__":
    run_and_export(
        F1CompleteGrandPrixScraper,
        "grands_prix/f1_grands_prix_extended.json",
        run_config=RunConfig(output_dir=Path("../../data/wiki")),
    )
