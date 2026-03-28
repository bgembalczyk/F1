from models.records.circuit import CIRCUIT_SCHEMA
from scrapers.base.composite_validator import SchemaCompositeRecordValidator


class CircuitsRecordValidator(SchemaCompositeRecordValidator):
    def __init__(self, record_factory=None) -> None:
        super().__init__(schema=CIRCUIT_SCHEMA, record_factory=record_factory)
