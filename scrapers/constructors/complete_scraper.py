from complete_extractor.base import CompleteExtractorBase
from complete_extractor.domain_config import CompleteExtractorDomainConfig
from scrapers.constructors.current_constructors_list import (
    CurrentConstructorsListScraper,
)
from scrapers.constructors.former_constructors_list import FormerConstructorsListScraper
from scrapers.constructors.indianapolis_only_constructors_list import (
    IndianapolisOnlyConstructorsListScraper,
)
from scrapers.constructors.privateer_teams_list import PrivateerTeamsListScraper
from scrapers.constructors.single_scraper import SingleConstructorScraper


class CompleteConstructorsDataExtractor(CompleteExtractorBase):
    """
    Uruchamia komplet list scraperów konstruktorów, a następnie dla każdego
    elementu pobiera szczegóły (infoboksy + tabele) za pomocą
    SingleConstructorScraper.
    """

    url = CurrentConstructorsListScraper.CONFIG.url
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_clses=(
            CurrentConstructorsListScraper,
            FormerConstructorsListScraper,
            IndianapolisOnlyConstructorsListScraper,
            PrivateerTeamsListScraper,
        ),
        single_scraper_cls=SingleConstructorScraper,
        detail_url_field_paths=("constructor.url", "constructor_url", "team_url"),
        filter_redlinks=True,
    )


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
