from models.records.grand_prix import validate_grands_prix_record
from validation.issue import ValidationIssue
from validation.validator_base import ExportRecord
from validation.validator_base import RecordValidator


class GrandsPrixRecordValidator(RecordValidator):
    def validate(self, record: ExportRecord) -> list[ValidationIssue]:
        return validate_grands_prix_record(record)
