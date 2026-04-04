from complete_extractor.base import CompleteExtractorBase
from complete_extractor.domain_config import CompleteExtractorDomainConfig
from scrapers.base.helpers.wiki import is_wikipedia_redlink
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
        list_scraper_classes=(ConstructorsListScraper,),
        single_scraper_cls=SingleConstructorScraper,
        detail_url_field_paths=("constructor.url", "constructor_url", "team_url"),
        filter_redlinks=True,
    )

    @classmethod
    def _get_constructor_url(cls, record: dict) -> str | None:
        """
        Back-compat helper for constructor detail URL resolution.

        Keeps URL lookup aligned with DOMAIN_CONFIG.detail_url_field_paths and
        redlink filtering policy used by complete extractors.
        """
        for field_path in cls.DOMAIN_CONFIG.detail_url_field_paths:
            value = cls._get_value_by_path(record, field_path)
            if not isinstance(value, str) or not value:
                continue
            if cls.DOMAIN_CONFIG.filter_redlinks and is_wikipedia_redlink(value):
                continue
            return value
        return None

    def get_detail_url(self, record: dict[str, object]) -> str | None:
        return self._get_constructor_url(record)
