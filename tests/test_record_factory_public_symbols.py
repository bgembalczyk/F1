from models.records.factories.mapping import MappingRecordFactory


def test_mapping_record_factory_is_publicly_importable() -> None:
    factory = MappingRecordFactory()

    assert factory.create({"a": 1}) == {"a": 1}
