from collections.abc import Sequence

from scrapers.options import ScraperOptions
from scrapers.transformers.record.base import RecordTransformer
from scrapers.transformers.record.normalize_links import NormalizeLinksTransformer


def build_transformers(
    transformers: Sequence[RecordTransformer] | None = None,
    *,
    include_defaults: bool = True,
) -> list[RecordTransformer]:
    resolved = list(transformers or [])
    if include_defaults and not any(
        isinstance(transformer, NormalizeLinksTransformer) for transformer in resolved
    ):
        resolved.insert(0, NormalizeLinksTransformer())
    return resolved


def append_transformer(
    options: ScraperOptions | None,
    transformer: RecordTransformer,
) -> ScraperOptions:
    resolved = options or ScraperOptions()
    resolved.pipeline.transformers = [
        *list(resolved.pipeline.transformers or []),
        transformer,
    ]
    return resolved
