"""DEPRECATED ENTRYPOINT: use scrapers.drivers.entrypoint.run_list_scraper."""

from pathlib import Path
import warnings

from models.records.factories import build_driver_record
from scrapers.base.helpers.config_factory import ScraperCommonConfig
from scrapers.base.helpers.config_factory import build_table_config
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.transformers.drivers_championships import (
    DriversChampionshipsTransformer,
)
from scrapers.drivers.columns.driver_name_status import DriverNameStatusColumn
from scrapers.drivers.constants import DRIVER_CHAMPIONSHIPS_HEADER
from scrapers.drivers.constants import DRIVER_FASTEST_LAPS_HEADER
from scrapers.drivers.constants import DRIVER_NAME_HEADER
from scrapers.drivers.constants import DRIVER_NATIONALITY_HEADER
from scrapers.drivers.constants import DRIVER_PODIUMS_HEADER
from scrapers.drivers.constants import DRIVER_POINTS_HEADER
from scrapers.drivers.constants import DRIVER_POLE_POSITIONS_HEADER
from scrapers.drivers.constants import DRIVER_RACE_ENTRIES_HEADER
from scrapers.drivers.constants import DRIVER_RACE_STARTS_HEADER
from scrapers.drivers.constants import DRIVER_RACE_WINS_HEADER
from scrapers.drivers.constants import DRIVER_SEASONS_COMPETED_HEADER
from scrapers.drivers.constants import DRIVERS_LIST_HEADERS
from scrapers.drivers.validator import DriversRecordValidator


class F1DriversListScraper(F1TableScraper):
    """
    Scraper listy kierowców F1 z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_drivers

    Dodatkowo:
    - is_active: (~ lub * na końcu raw_text w kolumnie "Driver name")
    - is_world_champion: (~ lub ^ na końcu raw_text w kolumnie "Driver name")
    - drivers_championships: parsowane do dict {count, seasons}
    """

    default_validator = DriversRecordValidator()

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_drivers",
        section_id="Drivers",
        expected_headers=DRIVERS_LIST_HEADERS,
        schema=TableSchemaDSL(
            columns=[
                column(DRIVER_NAME_HEADER, "driver", DriverNameStatusColumn()),
                column(DRIVER_NATIONALITY_HEADER, "nationality", TextColumn()),
                column(
                    DRIVER_SEASONS_COMPETED_HEADER,
                    "seasons_competed",
                    SeasonsColumn(),
                ),
                column(
                    DRIVER_CHAMPIONSHIPS_HEADER,
                    "drivers_championships",
                    TextColumn(),  # zparsujemy ręcznie w fetch()
                ),
                column(DRIVER_RACE_ENTRIES_HEADER, "race_entries", IntColumn()),
                column(DRIVER_RACE_STARTS_HEADER, "race_starts", IntColumn()),
                column(DRIVER_POLE_POSITIONS_HEADER, "pole_positions", IntColumn()),
                column(DRIVER_RACE_WINS_HEADER, "race_wins", IntColumn()),
                column(DRIVER_PODIUMS_HEADER, "podiums", IntColumn()),
                column(DRIVER_FASTEST_LAPS_HEADER, "fastest_laps", IntColumn()),
                column(DRIVER_POINTS_HEADER, "points", TextColumn()),
            ],
        ),
        record_factory=build_driver_record,
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: ScraperConfig | None = None,
    ) -> None:
        options = build_table_config(
            options,
            config=ScraperCommonConfig(
                include_urls=True,
                normalize_empty_values=False,
                validation_mode="hard",
            ),
        )
        options.transformers = [
            *list(options.transformers or []),
            DriversChampionshipsTransformer(),
        ]
        super().__init__(options=options, config=config)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quality-report",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Zapisz raport jakości do debug_dir/quality_report.json.",
    )
    parser.add_argument(
        "--error-report",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Zapisz raporty błędów do debug_dir/errors.jsonl.",
    )
    args = parser.parse_args()
    from scrapers.drivers.entrypoint import run_list_scraper

    warnings.warn(
        "scrapers.drivers.list_scraper is deprecated; use scrapers.drivers.entrypoint.run_list_scraper.",
        DeprecationWarning,
        stacklevel=2,
    )
    run_list_scraper(
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
            quality_report=args.quality_report,
            error_report=args.error_report,
        ),
    )
