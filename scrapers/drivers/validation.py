from validation.records import ExportRecord
from validation.records import RecordValidator


class DriversRecordValidator(RecordValidator):
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
