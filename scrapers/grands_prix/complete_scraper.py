from pathlib import Path
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.base.runner import RunConfig, run_and_export
from scrapers.base.scraper import F1Scraper
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.grands_prix.list_scraper import GrandsPrixListScraper
from scrapers.grands_prix.single_scraper import F1SingleGrandPrixScraper


class F1CompleteGrandPrixScraper(F1Scraper):
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

        html_adapter = options.with_source_adapter()
        policy = options.to_http_policy()

        super().__init__(options=options)

        self.list_scraper = GrandsPrixListScraper(
            options=ScraperOptions(
                include_urls=True,
                policy=policy,
                source_adapter=html_adapter,
            ),
        )
        self.single_scraper = F1SingleGrandPrixScraper(
            options=ScraperOptions(
                policy=policy,
                source_adapter=html_adapter,
            ),
        )
        self.grands_prix_adapter = IterableSourceAdapter(self.list_scraper.fetch)

    def fetch(self) -> List[Dict[str, Any]]:
        grands_prix = self.grands_prix_adapter.get()
        complete: List[Dict[str, Any]] = []

        for grand_prix in grands_prix:
            if not isinstance(grand_prix, dict):
                raise TypeError(
                    "GrandsPrixListScraper musi zwracać dict, "
                    f"otrzymano: {type(grand_prix).__name__}"
                )

            record = grand_prix

            grand_prix_url: Optional[str] = None
            race_title = record.get("race_title")
            if isinstance(race_title, dict):
                grand_prix_url = race_title.get("url")

            by_year: Optional[List[Dict[str, Any]]] = None
            if grand_prix_url:
                details_list = self.single_scraper.fetch_by_url(grand_prix_url)
                if details_list:
                    by_year = details_list[0].get("by_year")

            full_record = dict(record)
            full_record["by_year"] = by_year
            complete.append(full_record)

        self._data = complete
        return self._data

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Metoda wymagana przez bazę – nie używana w tym scraperze."""
        raise NotImplementedError("Use fetch() bezpośrednio dla pełnego scrapingu")


if __name__ == "__main__":
    run_and_export(
        F1CompleteGrandPrixScraper,
        "grands_prix/f1_grands_prix_extended.json",
        run_config=RunConfig(output_dir=Path("../../data/wiki")),
    )
