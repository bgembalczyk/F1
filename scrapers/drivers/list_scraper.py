"""DEPRECATED ENTRYPOINT: use scrapers.drivers.entrypoint.run_list_scraper."""

from models.records.factories.build import RECORD_BUILDERS
from scrapers.base.options import ScraperOptions
from scrapers.base.table.builders import build_columns
from scrapers.base.table.builders import build_metric_columns
from scrapers.base.table.builders import metric_column
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.seed_list_scraper import SeedListTableScraper
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


class F1DriversListScraper(SeedListTableScraper):
    domain = "drivers"
    default_output_path = "raw/drivers/seeds/complete_drivers"
    legacy_output_path = "drivers/complete_drivers"

    """
    Scraper listy kierowców F1 z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_drivers

    Dodatkowo:
    - is_active: (~ lub * na końcu raw_text w kolumnie "Driver name")
    - is_world_champion: (~ lub ^ na końcu raw_text w kolumnie "Driver name")
    - drivers_championships: parsowane do dict {count, seasons}
    """

    default_validator = DriversRecordValidator()
    options_profile = "strict_seed"

    schema_columns = build_columns(
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
        build_metric_columns(
            [
                metric_column(
                    DRIVER_RACE_ENTRIES_HEADER,
                    "race_entries",
                    "races_entered",
                ),
                metric_column(
                    DRIVER_RACE_STARTS_HEADER,
                    "race_starts",
                    "races_started",
                ),
                metric_column(
                    DRIVER_POLE_POSITIONS_HEADER,
                    "pole_positions",
                    "poles",
                ),
                metric_column(DRIVER_RACE_WINS_HEADER, "race_wins", "wins"),
                metric_column(DRIVER_PODIUMS_HEADER, "podiums", "podiums"),
                metric_column(
                    DRIVER_FASTEST_LAPS_HEADER,
                    "fastest_laps",
                    "fastest_laps",
                ),
                metric_column(DRIVER_POINTS_HEADER, "points", "points"),
            ],
            column_overrides={"points": TextColumn()},
        ),
    )

    CONFIG = SeedListTableScraper.build_config(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_drivers",
        section_id="Drivers",
        expected_headers=DRIVERS_LIST_HEADERS,
        columns=schema_columns,
        record_factory=RECORD_BUILDERS.driver,
    )

    def extend_options(self, options: ScraperOptions) -> ScraperOptions:
        options.transformers = [
            *list(options.transformers or []),
            DriversChampionshipsTransformer(),
        ]
        return options


if __name__ == "__main__":
    from scrapers.cli import run_current_legacy_wrapper

    run_current_legacy_wrapper()
