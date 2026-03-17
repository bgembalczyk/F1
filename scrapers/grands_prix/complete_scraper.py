from pathlib import Path

from scrapers.base.complete_extractor_base import CompleteExtractorBase
from scrapers.base.complete_extractor_base import CompleteExtractorDomainConfig
from scrapers.grands_prix.list_scraper import GrandsPrixListScraper
from scrapers.grands_prix.single_scraper import F1SingleGrandPrixScraper


class F1CompleteGrandPrixDataExtractor(CompleteExtractorBase):
    """
    Pobiera listę Grand Prix, a następnie zaciąga tabelę "By year"
    z każdego artykułu na Wikipedii, rozszerzając rekordy listy.

    Jeżeli artykuł nie wygląda na Grand Prix, pole `by_year` będzie None.
    """

    url = GrandsPrixListScraper.CONFIG.url
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_cls=GrandsPrixListScraper,
        single_scraper_cls=F1SingleGrandPrixScraper,
        detail_url_field_path="race_title.url",
        assemble_record_strategy="extract_detail_field",
        assemble_record_params={"detail_field": "by_year"},
    )


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
