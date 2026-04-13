from complete_extractor.composite_validator import SchemaCompositeRecordValidator
from models.records.driver import DRIVER_SCHEMA


class DriversRecordValidator(SchemaCompositeRecordValidator):
    def __init__(self, record_factory_validator=None) -> None:
        super().__init__(
            schema=DRIVER_SCHEMA,
            record_factory_validator=record_factory_validator,
        )
