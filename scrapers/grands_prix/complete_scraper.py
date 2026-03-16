from pathlib import Path
from typing import Any

from scrapers.base.composite_scraper import CompositeDataExtractor
from scrapers.base.composite_scraper import CompositeDataExtractorChildren
from scrapers.base.options import ScraperOptions
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.grands_prix.list_scraper import GrandsPrixListScraper
from scrapers.grands_prix.single_scraper import F1SingleGrandPrixScraper


class F1CompleteGrandPrixDataExtractor(CompositeDataExtractor):
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

    def build_children(self) -> CompositeDataExtractorChildren:
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

        return CompositeDataExtractorChildren(
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


if __name__ == "__main__":
    from scrapers.base.cli_entrypoint import build_cli_main
    from scrapers.base.helpers.runner import run_and_export
    from scrapers.base.run_config import RunConfig

    build_cli_main(
        target=lambda *, run_config: run_and_export(
            F1CompleteGrandPrixDataExtractor,
            "grands_prix/f1_grands_prix_extended.json",
            run_config=run_config,
        ),
        base_config=RunConfig(output_dir=Path("../../data/wiki")),
        profile="complete_extractor",
    )()
