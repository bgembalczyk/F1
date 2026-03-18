from models.records.grand_prix import GRANDS_PRIX_SCHEMA
from validation.issue import ValidationIssue
from validation.validator_base import ExportRecord
from validation.validator_base import RecordValidator


class GrandsPrixRecordValidator(RecordValidator):
    def validate(self, record: ExportRecord) -> list[ValidationIssue]:
        return self.validate_schema(record, GRANDS_PRIX_SCHEMA)
