from collections.abc import Sequence
from typing import Any

from scrapers.base.normalization_pipeline import NormalizationPlugin
from scrapers.base.normalization_pipeline import normalize_value


def normalize_auto_value(
    value: Any,
    *,
    strip_marks: bool = False,
    drop_empty: bool = True,
    plugins: Sequence[NormalizationPlugin] | None = None,
) -> Any:
    return normalize_value(
        value,
        strip_marks=strip_marks,
        drop_empty=drop_empty,
        drop_empty_text=drop_empty,
        plugins=plugins,
    )
