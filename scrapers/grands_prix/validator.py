from validation.records import ExportRecord
from validation.records import BaseDomainRecordValidator


class GrandsPrixRecordValidator(BaseDomainRecordValidator):
    def validate(self, record: ExportRecord) -> list[str]:
        errors: list[str] = []
        errors.extend(
            self.require_keys(
                record,
                ["race_title", "race_status", "years_held", "country", "total"],
            )
        )
        errors.extend(self.require_type(record, "race_title", dict))
        errors.extend(self.require_type(record, "race_status", str))
        errors.extend(self.require_type(record, "years_held", list))
        errors.extend(self.require_type(record, "country", list))
        errors.extend(self.require_type(record, "total", int, allow_none=True))
        errors.extend(self.require_type(record, "circuits", int, allow_none=True))

        race_title = record.get("race_title")
        if isinstance(race_title, dict):
            errors.extend(self.require_link_dict(race_title, "race_title"))

        country = record.get("country")
        if isinstance(country, list):
            errors.extend(self.require_link_list(country, "country"))

        return errors
