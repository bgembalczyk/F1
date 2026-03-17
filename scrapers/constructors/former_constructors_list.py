from pathlib import Path

from models.records.factories import build_constructor_record
from scrapers.base.run_config import RunConfig
from scrapers.constructors.base_constructor_list_scraper import BaseConstructorListScraper
from scrapers.constructors.constants import FORMER_CONSTRUCTORS_EXPECTED_HEADERS
from scrapers.constructors.schemas import build_former_constructors_schema
from scrapers.constructors.sections import ConstructorsListSectionParser
from scrapers.constructors.spec import CONSTRUCTORS_LIST_SPEC
from scrapers.constructors.spec import build_constructors_list_config


class FormerConstructorsListScraper(BaseConstructorListScraper):
    options_domain = CONSTRUCTORS_LIST_SPEC.domain
    options_profile = CONSTRUCTORS_LIST_SPEC.options_profile

    CONFIG = build_constructors_list_config(
        section_id="Former_constructors",
        expected_headers=FORMER_CONSTRUCTORS_EXPECTED_HEADERS,
        schema=build_former_constructors_schema(),
        record_factory=build_constructor_record,
    )

    section_label = "Former constructors"
    section_parser_class = ConstructorsListSectionParser


if __name__ == "__main__":
    from scrapers.base.cli_entrypoint import run_cli_entrypoint
    from scrapers.base.helpers.runner import run_and_export

    run_cli_entrypoint(
        target=lambda *, run_config: run_and_export(
            FormerConstructorsListScraper,
            "constructors/f1_former_constructors.json",
            "constructors/f1_former_constructors.csv",
            run_config=run_config,
        ),
        base_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
        ),
    )
