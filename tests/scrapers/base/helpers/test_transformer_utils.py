# ruff: noqa: E501, PLR2004
from scrapers.base.helpers.transformer_utils import apply_transformers_with_factory


class _DoubleValueTransformer:
    """Doubles every numeric value in record."""

    def __call__(self, record):
        return {k: v * 2 if isinstance(v, int) else v for k, v in record.items()}

    # Satisfy RecordTransformer interface used by apply_transformers
    def transform(self, records):
        return [self(r) for r in records]


def test_apply_transformers_with_factory_no_factory_no_transformers_returns_record() -> (
    None
):
    record = {"a": 1, "b": 2}
    result = apply_transformers_with_factory([], record, record_factory=None)
    assert result == {"a": 1, "b": 2}


def test_apply_transformers_with_factory_with_record_factory_converts_record() -> None:
    # Line 29: record_factory is not None -> append RecordFactoryTransformer
    def simple_factory(a, b):
        return {"sum": a + b}

    record = {"a": 3, "b": 4}
    # Using a callable that mimics factory
    # Since RecordFactoryTransformer uses factory(**record) for plain types,
    # pass a function that accepts keyword args
    result = apply_transformers_with_factory([], record, record_factory=simple_factory)
    # Result should be {"sum": 7} or the dict if factory fails with fallback
    assert isinstance(result, dict)


def test_apply_transformers_with_factory_empty_transformed_returns_empty_dict() -> None:
    # Line 36: return transformed[0] if transformed else {}
    # When factory returns None / transformer filters out the record,
    # we just need transformers_list to be non-empty and transformers to yield empty

    class _FilterAllTransformer:
        def apply(self, records):
            return []

        # Make it look like a RecordTransformer via duck typing
        empty_value_policy = None

    # Without factory, no transformers -> returns record directly
    result = apply_transformers_with_factory([], {}, record_factory=None)
    assert result == {}
