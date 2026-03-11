from collections.abc import Sequence

from scrapers.base.transformers.normalize_links import NormalizeLinksTransformer
from scrapers.base.transformers.record_transformer import RecordTransformer


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
