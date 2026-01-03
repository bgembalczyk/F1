from typing import Any, Optional, TypedDict

from scrapers.base.validation import RecordValidator

from models.records.driver_championships import DriversChampionshipsRecord
from models.records.link import LinkRecord
from models.records.season import SeasonRecord


class DriverRecord(TypedDict, total=False):
    driver: LinkRecord
    is_active: bool
    is_world_champion: bool
    nationality: Optional[str]
    seasons_competed: list[SeasonRecord]
    drivers_championships: DriversChampionshipsRecord
    race_entries: Optional[int]
    race_starts: Optional[int]
    pole_positions: Optional[int]
    race_wins: Optional[int]
    podiums: Optional[int]
    fastest_laps: Optional[int]
    points: Optional[str]

    @classmethod
    def validate_record(cls, record: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        errors.extend(
            RecordValidator.require_keys(
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
        errors.extend(RecordValidator.require_type(record, "driver", dict))
        errors.extend(RecordValidator.require_type(record, "nationality", str))
        errors.extend(RecordValidator.require_type(record, "seasons_competed", list))
        errors.extend(
            RecordValidator.require_type(record, "drivers_championships", dict)
        )
        errors.extend(RecordValidator.require_type(record, "is_active", bool))
        errors.extend(RecordValidator.require_type(record, "is_world_champion", bool))

        driver = record.get("driver")
        if isinstance(driver, dict):
            errors.extend(RecordValidator.require_link_dict(driver, "driver"))

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
