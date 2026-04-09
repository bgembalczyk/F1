from models.records.circuit import CIRCUIT_SCHEMA
from scrapers.base.composite_validator import SchemaCompositeRecordValidator


class CircuitsRecordValidator(SchemaCompositeRecordValidator):
    def __init__(self, record_factory_validator=None) -> None:
        super().__init__(
            schema=CIRCUIT_SCHEMA,
            record_factory_validator=record_factory_validator,
        )
