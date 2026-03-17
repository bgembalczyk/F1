"""DEPRECATED ENTRYPOINT: use scrapers.drivers.entrypoint.run_list_scraper."""

from pathlib import Path

from models.records.factories import build_driver_record
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.transformers.drivers_championships import DriversChampionshipsTransformer
from scrapers.drivers.constants import DRIVERS_LIST_HEADERS
from scrapers.drivers.schemas import build_drivers_list_schema
from scrapers.drivers.spec import DRIVERS_LIST_SPEC
from scrapers.drivers.spec import build_drivers_list_config


class F1DriversListScraper(F1TableScraper):
    default_validator = DRIVERS_LIST_SPEC.default_validator
    options_domain = DRIVERS_LIST_SPEC.domain
    options_profile = DRIVERS_LIST_SPEC.options_profile

    CONFIG = build_drivers_list_config(
        expected_headers=DRIVERS_LIST_HEADERS,
        schema=build_drivers_list_schema(),
        record_factory=build_driver_record,
    )

    def __init__(self, *, options: ScraperOptions | None = None, config: ScraperConfig | None = None) -> None:
        super().__init__(options=options, config=config)

    def extend_options(self, options: ScraperOptions) -> ScraperOptions:
        options.transformers = [*list(options.transformers or []), DriversChampionshipsTransformer()]
        return options


if __name__ == "__main__":
    from scrapers.base.cli_entrypoint import build_cli_main
    from scrapers.drivers.entrypoint import run_list_scraper

    build_cli_main(
        target=run_list_scraper,
        base_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
        ),
        profile="deprecated_entrypoint",
        deprecation_message=(
            "scrapers.drivers.list_scraper is deprecated; use "
            "scrapers.drivers.entrypoint.run_list_scraper."
        ),
    )()
