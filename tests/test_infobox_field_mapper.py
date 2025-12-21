from scrapers.base.infobox.field_mapper import InfoboxFieldMapper


def test_mapper_returns_raw_payload():
    mapper = InfoboxFieldMapper()
    raw = {"title": "Sample", "rows": {"Key": {"text": "Value", "links": []}}}

    assert mapper.map(raw) == raw


def test_mapper_normalizes_missing_payload():
    mapper = InfoboxFieldMapper()

    assert mapper.map(None) == {"title": None, "rows": {}}
    assert mapper.map({}) == {"title": None, "rows": {}}
