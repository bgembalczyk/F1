from scrapers.base.complete_extractor import CompleteExtractorBase
from scrapers.base.complete_extractor import CompleteExtractorDomainConfig
from scrapers.base.complete_extractor import ExtractDetailFieldStrategy
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
        record_assembly_strategy=ExtractDetailFieldStrategy(detail_field="by_year"),
    )


if __name__ == "__main__":
    from scrapers.cli import run_legacy_wrapper

    run_legacy_wrapper("scrapers.grands_prix.complete_scraper")
