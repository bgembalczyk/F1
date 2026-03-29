from validation.composite_validator import CompositeRecordValidator
from validation.rules import build_common_rules
from validation.schema_rules import build_domain_rules
from validation.schemas import RecordSchema


class SchemaCompositeRecordValidator(CompositeRecordValidator):
    def __init__(self, schema, record_factory=None) -> None:
        normalized = RecordSchema.from_mapping(schema)
        super().__init__(
            record_factory=record_factory,
            common_rules=build_common_rules(
                required=normalized.required,
                types=normalized.types,
                allow_none=normalized.allow_none,
            ),
            domain_rules=build_domain_rules(normalized),
        )
