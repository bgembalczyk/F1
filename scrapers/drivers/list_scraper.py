from pathlib import Path
from typing import Any, List

from models.records.driver_championships import DriversChampionshipsRecord
from models.records.factories import build_driver_record
from models.services.driver_service import DriverService
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from validation.records import ExportRecord
from scrapers.base.transformers import RecordTransformer
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.table.schema import TableSchemaBuilder
from scrapers.drivers.columns.driver_name_status import DriverNameStatusColumn
from scrapers.drivers.constants import (
    DRIVER_NAME_HEADER,
    DRIVERS_CHAMPIONSHIPS_HEADER,
    DRIVERS_LIST_HEADERS,
    FASTEST_LAPS_HEADER,
    NATIONALITY_HEADER,
    PODIUMS_HEADER,
    POLE_POSITIONS_HEADER,
    POINTS_HEADER,
    RACE_ENTRIES_HEADER,
    RACE_STARTS_HEADER,
    RACE_WINS_HEADER,
    SEASONS_COMPETED_HEADER,
)
from scrapers.drivers.transformers.drivers_championships import DriversChampionshipsTransformer
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
        schema=(
            TableSchemaBuilder()
            .map(DRIVER_NAME_HEADER, "driver", DriverNameStatusColumn())
            .map(NATIONALITY_HEADER, "nationality", TextColumn())
            .map(SEASONS_COMPETED_HEADER, "seasons_competed", SeasonsColumn())
            .map(
                DRIVERS_CHAMPIONSHIPS_HEADER,
                "drivers_championships",
                TextColumn(),  # zparsujemy ręcznie w fetch()
            )
            .map(RACE_ENTRIES_HEADER, "race_entries", IntColumn())
            .map(RACE_STARTS_HEADER, "race_starts", IntColumn())
            .map(POLE_POSITIONS_HEADER, "pole_positions", IntColumn())
            .map(RACE_WINS_HEADER, "race_wins", IntColumn())
            .map(PODIUMS_HEADER, "podiums", IntColumn())
            .map(FASTEST_LAPS_HEADER, "fastest_laps", IntColumn())
            .map(POINTS_HEADER, "points", TextColumn())
        ),
        record_factory=build_driver_record,
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: ScraperConfig | None = None,
    ) -> None:
        options = options or ScraperOptions()
        options.validation_mode = "hard"
        options.normalize_empty_values = False
        super().__init__(options=options, config=config)
        self.transformers = [DriversChampionshipsTransformer()]


if __name__ == "__main__":
    run_and_export(
        F1DriversListScraper,
        "drivers/f1_drivers.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
        ),
    )
