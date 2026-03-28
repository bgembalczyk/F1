from models.records.driver import DRIVER_SCHEMA
from validation.composite_validator import CompositeRecordValidator
from validation.rules import build_common_rules
from validation.schema_rules import build_domain_rules
from validation.validator_base import RecordValidator

_NORMALIZED = RecordValidator._coerce_schema(DRIVER_SCHEMA)


class DriversRecordValidator(CompositeRecordValidator):
    def __init__(self, record_factory=None) -> None:
        super().__init__(
            record_factory=record_factory,
            common_rules=build_common_rules(
                required=_NORMALIZED.required,
                types=_NORMALIZED.types,
                allow_none=_NORMALIZED.allow_none,
            ),
            domain_rules=build_domain_rules(_NORMALIZED),
        )
