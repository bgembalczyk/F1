from collections.abc import Sequence

from scrapers.base.normalization import NormalizationRule
from scrapers.base.normalization import RecordNormalizer
from scrapers.base.results import ScrapeResult


class ScrapeResultNormalizer:
    def normalize(
        self,
        result: ScrapeResult,
        *,
        normalize_keys: bool = False,
        normalization_rules: Sequence[NormalizationRule] | None = None,
    ) -> ScrapeResult:
        normalizer = RecordNormalizer(
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )
        if not normalizer.has_rules:
            return result

        normalized = normalizer.normalize(result.data)
        return ScrapeResult(
            data=normalized,
            source_url=result.source_url,
            timestamp=result.timestamp,
        )
