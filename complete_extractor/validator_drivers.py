from models.records.driver import DRIVER_SCHEMA
from validation.rules import build_common_rules
from validation.schema_rules import build_domain_rules
from validation.validator_base import RecordValidator


class DriversRecordValidator(RecordValidator):
    def __init__(self, record_factory_validator=None) -> None:
        normalized = RecordValidator._coerce_schema(DRIVER_SCHEMA)  # noqa: SLF001
        super().__init__(
            record_factory_validator=record_factory_validator,
            common_rules=build_common_rules(
                required=normalized.required,
                types=normalized.types,
                allow_none=normalized.allow_none,
            ),
            domain_rules=build_domain_rules(normalized),
        )
