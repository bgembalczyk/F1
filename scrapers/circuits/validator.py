from models.records.circuit import CIRCUIT_SCHEMA
from validation.issue import ValidationIssue
from validation.validator_base import ExportRecord
from validation.validator_base import RecordValidator


class CircuitsRecordValidator(RecordValidator):
    def validate(self, record: ExportRecord) -> list[ValidationIssue]:
        return self.validate_schema(record, CIRCUIT_SCHEMA)
