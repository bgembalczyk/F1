class DoubleValueTransformer:
    """Doubles every numeric value in record."""

    def __call__(self, record):
        return {k: v * 2 if isinstance(v, int) else v for k, v in record.items()}

    # Satisfy RecordTransformer interface used by apply_transformers
    def transform(self, _records):
        return [self(r) for r in _records]

