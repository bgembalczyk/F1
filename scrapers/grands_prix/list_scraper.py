"""DEPRECATED ENTRYPOINT: use scrapers.grands_prix.entrypoint.run_list_scraper."""

from models.records.factories import build_grands_prix_record
from scrapers.base.options import ScraperOptions
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.grands_prix.schemas import build_grands_prix_list_schema
from scrapers.grands_prix.spec import GRANDS_PRIX_LIST_SPEC
from scrapers.grands_prix.spec import build_grands_prix_list_config


class GrandsPrixListScraper(F1TableScraper):
    default_validator = GRANDS_PRIX_LIST_SPEC.default_validator
    options_domain = GRANDS_PRIX_LIST_SPEC.domain
    options_profile = GRANDS_PRIX_LIST_SPEC.options_profile

    CONFIG = build_grands_prix_list_config(
        expected_headers=["Race title", "Years held"],
        schema=build_grands_prix_list_schema(),
        record_factory=build_grands_prix_record,
    )

    def __init__(self, *, options: ScraperOptions | None = None, config: ScraperConfig | None = None) -> None:
        super().__init__(options=options, config=config)


if __name__ == "__main__":
    from scrapers.base.cli_entrypoint import build_deprecated_module_main
    from scrapers.grands_prix.entrypoint import run_list_scraper

    build_deprecated_module_main(
        target=run_list_scraper,
        deprecation_message=(
            "scrapers.grands_prix.list_scraper is deprecated; use "
            "scrapers.grands_prix.entrypoint.run_list_scraper."
        ),
    )()
