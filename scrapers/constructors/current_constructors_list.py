"""DEPRECATED ENTRYPOINT: use scrapers.constructors.entrypoint.run_list_scraper."""

from datetime import datetime
from datetime import timezone
from pathlib import Path

from models.records.factories import build_constructor_record
from scrapers.base.run_config import RunConfig
from scrapers.constructors.base_constructor_list_scraper import BaseConstructorListScraper
from scrapers.constructors.constants import CURRENT_CONSTRUCTORS_EXPECTED_HEADERS
from scrapers.constructors.schemas import build_current_constructors_schema
from scrapers.constructors.sections import ConstructorsListSectionParser
from scrapers.constructors.spec import CONSTRUCTORS_LIST_SPEC
from scrapers.constructors.spec import build_constructors_list_config

CURRENT_YEAR = datetime.now(tz=timezone.utc).year


class CurrentConstructorsListScraper(BaseConstructorListScraper):
    options_domain = CONSTRUCTORS_LIST_SPEC.domain
    options_profile = CONSTRUCTORS_LIST_SPEC.options_profile

    CONFIG = build_constructors_list_config(
        section_id=f"Constructors_for_the_{CURRENT_YEAR}_season",
        expected_headers=CURRENT_CONSTRUCTORS_EXPECTED_HEADERS,
        schema=build_current_constructors_schema(),
        record_factory=build_constructor_record,
    )

    section_label = "Current constructors"
    section_parser_class = ConstructorsListSectionParser


if __name__ == "__main__":
    from scrapers.base.cli_entrypoint import build_cli_main
    from scrapers.constructors.entrypoint import run_list_scraper

    build_cli_main(
        target=run_list_scraper,
        base_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
        ),
        profile="deprecated_entrypoint",
        deprecation_message=(
            "scrapers.constructors.current_constructors_list is deprecated as "
            "an entrypoint; use scrapers.constructors.entrypoint.run_list_scraper."
        ),
    )()
