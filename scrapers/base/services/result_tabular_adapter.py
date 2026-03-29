from collections.abc import Sequence
from typing import Any

from scrapers.base.format.pandas_formatter import PandasDataFrameFormatter
from scrapers.base.normalization import NormalizationRule
from scrapers.base.results import ScrapeResult
from scrapers.base.services.result_normalizer import ScrapeResultNormalizer


class ResultTabularAdapter:
    def __init__(
        self,
        *,
        normalizer: ScrapeResultNormalizer | None = None,
        formatter: PandasDataFrameFormatter | None = None,
    ) -> None:
        self._normalizer = normalizer or ScrapeResultNormalizer()
        self._formatter = formatter or PandasDataFrameFormatter()

    def to_dataframe(
        self,
        result: ScrapeResult,
        *,
        normalize_keys: bool = False,
        normalization_rules: Sequence[NormalizationRule] | None = None,
    ) -> Any:
        normalized = self._normalizer.normalize(
            result,
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )
        return self._formatter.format(normalized)
