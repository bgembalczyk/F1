from scrapers.infobox.field.mapper import InfoboxFieldMapper
from scrapers.infobox.schemas.schema import InfoboxSchema
from scrapers.infobox.schemas.schema import InfoboxSchemaField


def test_mapper_returns_raw_payload():
    mapper = InfoboxFieldMapper()
    raw = {"title": "Sample", "rows": {"Key": {"text": "Value", "links": []}}}

    assert mapper.map(raw) == raw


def test_mapper_normalizes_missing_payload():
    mapper = InfoboxFieldMapper()

    assert mapper.map(None) == {"title": None, "rows": {}}
    assert mapper.map({}) == {"title": None, "rows": {}}


def test_mapper_applies_schema_to_rows():
    schema = InfoboxSchema(
        name="test",
        fields=[InfoboxSchemaField(key="location", labels=("Location",))],
    )
    mapper = InfoboxFieldMapper(schema=schema)
    raw = {"title": "Sample", "rows": {"Location": {"text": "Value", "links": []}}}

    mapped = mapper.map(raw)

    assert mapped["rows"]["location"]["text"] == "Value"
