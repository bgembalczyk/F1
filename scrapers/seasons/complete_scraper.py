from pathlib import Path

from scrapers.base.complete_extractor_base import CompleteExtractorBase
from scrapers.base.complete_extractor_base import CompleteExtractorDomainConfig
from scrapers.seasons.list_scraper import SeasonsListScraper
from scrapers.seasons.single_scraper import SingleSeasonScraper


class CompleteSeasonDataExtractor(CompleteExtractorBase):
    url = SeasonsListScraper.CONFIG.url
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_cls=SeasonsListScraper,
        single_scraper_cls=SingleSeasonScraper,
        detail_url_field_path="season.url",
        assemble_record_strategy="bundle",
        assemble_record_params={
            "record_field": "season",
            "details_key": "tables",
            "details_default": {},
        },
    )

if __name__ == "__main__":
    from scrapers.cli import run_legacy_wrapper

    run_legacy_wrapper("scrapers.seasons.complete_scraper")
