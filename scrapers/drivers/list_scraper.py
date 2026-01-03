from pathlib import Path
from typing import Any, List

from models.scrape_types.driver_championships_payload import DriverChampionshipsPayload
from models.services.driver_service import DriverService
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.records import ExportRecord
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
    NATIONALITY_HEADER,
    SEASONS_COMPETED_HEADER,
)
from scrapers.drivers.validation import DriversRecordValidator


class DriversChampionshipsTransformer(RecordTransformer):
    @staticmethod
    def _parse_drivers_championships(raw: Any) -> DriverChampionshipsPayload:
        """
        Deleguje parsowanie do DriverService.parse_championships.

        Wejście (po TextColumn) bywa np.:
        - "0"
        - "2\\n2005–2006"
        - "7\\n1994–1995, 2000–2004"
        """
        return DriverService.parse_championships(raw)  # type: ignore[return-value]

    def transform(self, records: List[ExportRecord]) -> List[ExportRecord]:
        for row in records:
            champs_raw = row.get("drivers_championships")
            row["drivers_championships"] = self._parse_drivers_championships(champs_raw)
        return records


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
            .map("Race entries", "race_entries", IntColumn())
            .map("Race starts", "race_starts", IntColumn())
            .map("Pole positions", "pole_positions", IntColumn())
            .map("Race wins", "race_wins", IntColumn())
            .map("Podiums", "podiums", IntColumn())
            .map("Fastest laps", "fastest_laps", IntColumn())
            .map("Points", "points", TextColumn())
        ),
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: ScraperConfig | None = None,
    ) -> None:
        options = options or ScraperOptions()
        options.validation_mode = "hard"
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
