from complete_extractor.composite_validator import SchemaCompositeRecordValidator
from models.records.grand_prix import GRANDS_PRIX_SCHEMA


class GrandsPrixRecordValidator(SchemaCompositeRecordValidator):
    def __init__(self, record_factory_validator=None) -> None:
        super().__init__(
            schema=GRANDS_PRIX_SCHEMA,
            record_factory_validator=record_factory_validator,
        )
