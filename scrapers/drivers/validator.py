from models.records.driver import DRIVER_SCHEMA
from scrapers.base.composite_validator import SchemaCompositeRecordValidator


class DriversRecordValidator(SchemaCompositeRecordValidator):
    def __init__(self, record_factory=None) -> None:
        super().__init__(schema=DRIVER_SCHEMA, record_factory=record_factory)
