from complete_extractor.base import CompleteExtractorBase
from complete_extractor.domain_config import CompleteExtractorDomainConfig
from record_assembly_strategy.extract_detail_field import ExtractDetailFieldStrategy
from scrapers.grands_prix.list_scraper import GrandsPrixListScraper
from scrapers.grands_prix.single_scraper import GrandsPrixDetailScraper
from scrapers.component_metadata_wiki import COMPLETE_SCRAPER_KIND
from scrapers.component_metadata_wiki import build_component_metadata


class F1CompleteGrandPrixDataExtractor(CompleteExtractorBase):
    """
    Pobiera listę Grand Prix, a następnie zaciąga tabelę "By year"
    z każdego artykułu na Wikipedii, rozszerzając rekordy listy.

    Jeżeli artykuł nie wygląda na Grand Prix, pole `by_year` będzie None.
    """

    COMPONENT_METADATA = build_component_metadata(
        domain="grands_prix",
        kind=COMPLETE_SCRAPER_KIND,
    )
    url = GrandsPrixListScraper.CONFIG.url
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_classes=(GrandsPrixListScraper,),
        single_scraper_cls=GrandsPrixDetailScraper,
        detail_url_field_paths=("race_title.url",),
        record_assembly_strategy=ExtractDetailFieldStrategy(detail_field="by_year"),
    )
