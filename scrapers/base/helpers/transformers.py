from __future__ import annotations

from collections.abc import Sequence

from scrapers.base.transformers import RecordTransformer
from scrapers.base.transformers.normalize_links import NormalizeLinksTransformer


def build_transformers(
    transformers: Sequence[RecordTransformer] | None = None,
    *,
    include_defaults: bool = True,
) -> list[RecordTransformer]:
    resolved = list(transformers or [])
    if include_defaults and not any(
        isinstance(transformer, NormalizeLinksTransformer)
        for transformer in resolved
    ):
        resolved.insert(0, NormalizeLinksTransformer())
    return resolved
