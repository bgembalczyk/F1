from pathlib import Path

from models.records.factories import build_engine_manufacturer_record
from models.validation.engine_manufacturer import EngineManufacturer
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.engines.schemas import build_engine_manufacturers_schema
from scrapers.engines.spec import ENGINES_LIST_SPEC
from scrapers.engines.spec import build_engine_manufacturers_config


class EngineManufacturersListScraper(F1TableScraper):
    options_domain = ENGINES_LIST_SPEC.domain
    options_profile = ENGINES_LIST_SPEC.options_profile

    CONFIG = build_engine_manufacturers_config(
        expected_headers=[
            "Manufacturer",
            "Engines built in",
            "Seasons",
            "Races Entered",
            "Races Started",
            "Wins",
            "Points",
        ],
        record_factory=build_engine_manufacturer_record,
        model_class=EngineManufacturer,
        schema=build_engine_manufacturers_schema(),
    )


if __name__ == "__main__":
    run_and_export(
        EngineManufacturersListScraper,
        "engines/f1_engine_manufacturers.json",
        "engines/f1_engine_manufacturers.csv",
        run_config=RunConfig(output_dir=Path("../../data/wiki"), include_urls=True),
    )
