from validation.records import ExportRecord
from validation.records import BaseDomainRecordValidator


class CircuitsRecordValidator(BaseDomainRecordValidator):
    def validate(self, record: ExportRecord) -> list[str]:
        errors: list[str] = []
        errors.extend(
            self.require_keys(
                record,
                ["circuit", "circuit_status", "country", "seasons"],
            )
        )
        errors.extend(self.require_type(record, "circuit", dict))
        errors.extend(self.require_type(record, "circuit_status", str))
        errors.extend(self.require_type(record, "country", (str, dict)))
        errors.extend(self.require_type(record, "seasons", list))
        errors.extend(self.require_type(record, "grands_prix", list, allow_none=True))

        circuit = record.get("circuit")
        if isinstance(circuit, dict):
            errors.extend(self.require_link_dict(circuit, "circuit"))

        grands_prix = record.get("grands_prix")
        if isinstance(grands_prix, list):
            errors.extend(self.require_link_list(grands_prix, "grands_prix"))

        return errors
