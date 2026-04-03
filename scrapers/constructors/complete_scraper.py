from complete_extractor.base import CompleteExtractorBase
from complete_extractor.domain_config import CompleteExtractorDomainConfig
from scrapers.constructors.constructors_list import ConstructorsListScraper
from scrapers.constructors.single_scraper import SingleConstructorScraper
from scrapers.wiki.component_metadata import COMPLETE_SCRAPER_KIND
from scrapers.wiki.component_metadata import build_component_metadata


class CompleteConstructorsDataExtractor(CompleteExtractorBase):
    """
    Uruchamia komplet list scraperów konstruktorów, a następnie dla każdego
    elementu pobiera szczegóły (infoboksy + tabele) za pomocą
    SingleConstructorScraper.
    """

    COMPONENT_METADATA = build_component_metadata(
        domain="constructors",
        kind=COMPLETE_SCRAPER_KIND,
    )
    url = ConstructorsListScraper.url
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_classes=(
            ConstructorsListScraper,
        ),
        single_scraper_cls=SingleConstructorScraper,
        detail_url_field_paths=("constructor.url", "constructor_url", "team_url"),
        filter_redlinks=True,
    )
