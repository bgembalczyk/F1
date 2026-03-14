from collections.abc import Sequence

from scrapers.base.transformers.pipeline import TransformersPipeline
from scrapers.base.transformers.record_transformer import RecordTransformer
from validation.records import ExportRecord


def apply_transformers(
    transformers: Sequence[RecordTransformer],
    records: list[ExportRecord],
    *,
    logger=None,
) -> list[ExportRecord]:
    pipeline = TransformersPipeline(transformers, logger=logger)
    return pipeline.apply(records)
