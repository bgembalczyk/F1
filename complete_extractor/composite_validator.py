from validation.composite_validator import CompositeRecordValidator
from validation.record_factory_validator import RecordFactoryValidatorProtocol
from validation.rules import build_common_rules
from validation.schema_rules import build_domain_rules
from validation.validator_base import RecordValidator


class SchemaCompositeRecordValidator(CompositeRecordValidator):
    def __init__(
        self,
        schema,
        record_factory_validator: RecordFactoryValidatorProtocol | None = None,
    ) -> None:
        normalized = RecordValidator._coerce_schema(schema)  # noqa: SLF001
        super().__init__(
            record_factory_validator=record_factory_validator,
            common_rules=build_common_rules(
                required=normalized.required,
                types=normalized.types,
                allow_none=normalized.allow_none,
            ),
            domain_rules=build_domain_rules(normalized),
        )
