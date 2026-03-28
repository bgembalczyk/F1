from models.records.grand_prix import GRANDS_PRIX_SCHEMA
from scrapers.base.composite_validator import SchemaCompositeRecordValidator


class GrandsPrixRecordValidator(SchemaCompositeRecordValidator):
    def __init__(self, record_factory=None) -> None:
        super().__init__(schema=GRANDS_PRIX_SCHEMA, record_factory=record_factory)
