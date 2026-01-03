from pathlib import Path
from typing import Any, List

from models.scrape_types.driver_championships_payload import DriverChampionshipsPayload
from models.services.driver_service import DriverService
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.records import ExportRecord
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.table.schema import TableSchemaBuilder
from scrapers.base.validation import RecordValidator
from scrapers.drivers.columns.driver_name_status import DriverNameStatusColumn


class DriversListValidator(RecordValidator):
    def validate(self, record: ExportRecord) -> list[str]:
        errors: list[str] = []
        errors.extend(
            self.require_keys(
                record,
                [
                    "driver",
                    "nationality",
                    "seasons_competed",
                    "drivers_championships",
                    "is_active",
                    "is_world_champion",
                ],
            )
        )
        errors.extend(self.require_type(record, "driver", dict))
        errors.extend(self.require_type(record, "nationality", str))
        errors.extend(self.require_type(record, "seasons_competed", list))
        errors.extend(self.require_type(record, "drivers_championships", dict))
        errors.extend(self.require_type(record, "is_active", bool))
        errors.extend(self.require_type(record, "is_world_champion", bool))

        driver = record.get("driver")
        if isinstance(driver, dict):
            errors.extend(self.require_link_dict(driver, "driver"))

        championships = record.get("drivers_championships")
        if isinstance(championships, dict):
            if "count" not in championships:
                errors.append("drivers_championships.count is missing")
            elif not isinstance(championships.get("count"), int):
                errors.append("drivers_championships.count must be int")
            if "seasons" not in championships:
                errors.append("drivers_championships.seasons is missing")
            elif not isinstance(championships.get("seasons"), list):
                errors.append("drivers_championships.seasons must be list")

        return errors


class F1DriversListScraper(F1TableScraper):
    """
    Scraper listy kierowców F1 z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_drivers

    Dodatkowo:
    - is_active: (~ lub * na końcu raw_text w kolumnie "Driver name")
    - is_world_champion: (~ lub ^ na końcu raw_text w kolumnie "Driver name")
    - drivers_championships: parsowane do dict {count, seasons}
    """

    default_validator = DriversListValidator()

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_drivers",
        section_id="Drivers",
        expected_headers=[
            "Driver name",
            "Nationality",
            "Seasons competed",
            "Drivers' Championships",
        ],
        schema=(
            TableSchemaBuilder()
            .map("Driver name", "driver", DriverNameStatusColumn())
            .map("Nationality", "nationality", TextColumn())
            .map("Seasons competed", "seasons_competed", SeasonsColumn())
            .map(
                "Drivers' Championships",
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

    def post_process_records(self, records: List[ExportRecord]) -> List[ExportRecord]:
        before_count = len(records)
        self.logger.debug("Post-processing driver records: %d", before_count)

        for row in records:
            champs_raw = row.get("drivers_championships")
            row["drivers_championships"] = self._parse_drivers_championships(champs_raw)

        self.logger.debug(
            "Post-processing driver records complete: %d -> %d",
            before_count,
            len(records),
        )
        # runtime: nadal zwracamy list[dict], typy są dla Ciebie
        return records  # type: ignore[return-value]


if __name__ == "__main__":
    run_and_export(
        F1DriversListScraper,
        "drivers/f1_drivers.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
