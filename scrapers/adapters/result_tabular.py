from collections.abc import Sequence
from typing import Any

from scrapers.formatters.pandas import PandasDataFrameFormatter
from scrapers.normalization_utils import NormalizationRule
from scrapers.normalizers.result import ScrapeResultNormalizer
from scrapers.results import ScrapeResult


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
