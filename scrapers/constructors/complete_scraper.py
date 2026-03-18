from complete_extractor.base import CompleteExtractorBase
from complete_extractor.domain_config import CompleteExtractorDomainConfig
from scrapers.base.helpers.wiki import is_wikipedia_redlink
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

    @staticmethod
    def _get_constructor_url(record: dict[str, object]) -> str | None:
        config = CompleteConstructorsDataExtractor.DOMAIN_CONFIG
        for field_path in config.get_detail_url_field_paths():
            value = CompleteConstructorsDataExtractor._get_value_by_path(
                record,
                field_path,
            )
            if isinstance(value, str) and value:
                if config.filter_redlinks and is_wikipedia_redlink(value):
                    continue
                return value
        return None

    def get_detail_url(self, record: dict[str, object]) -> str | None:
        return self._get_constructor_url(record)


if __name__ == "__main__":
    from scrapers.cli import run_legacy_wrapper

    run_legacy_wrapper("scrapers.constructors.complete_scraper")
