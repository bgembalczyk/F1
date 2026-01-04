from __future__ import annotations

from typing import Sequence

from scrapers.base.transformers.normalize_links import NormalizeLinksTransformer
from scrapers.base.transformers.record_factory import RecordFactoryTransformer
from scrapers.base.transformers.record_transformer import RecordTransformer
from scrapers.base.transformers.pipeline import TransformersPipeline
from validation.records import ExportRecord


def apply_transformers(
    transformers: Sequence[RecordTransformer],
    records: list[ExportRecord],
    *,
    logger=None,
) -> list[ExportRecord]:
    pipeline = TransformersPipeline(transformers, logger=logger)
    return pipeline.apply(records)


__all__ = [
    "RecordTransformer",
    "TransformersPipeline",
    "RecordFactoryTransformer",
    "NormalizeLinksTransformer",
    "apply_transformers",
]
