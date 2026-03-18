from models.records.driver import DRIVER_SCHEMA
from validation.issue import ValidationIssue
from validation.validator_base import ExportRecord
from validation.validator_base import RecordValidator


class DriversRecordValidator(RecordValidator):
    def validate(self, record: ExportRecord) -> list[ValidationIssue]:
        return self.validate_schema(record, DRIVER_SCHEMA)
