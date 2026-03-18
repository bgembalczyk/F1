from complete_extractor import CompleteExtractorBase as LegacyCompleteExtractorBase
from complete_extractor.domain_config import (
    CompleteExtractorDomainConfig as LegacyCompleteExtractorDomainConfig,
)
from scrapers.base.complete_extractor import CompleteExtractorBase
from scrapers.base.complete_extractor import CompleteExtractorDomainConfig


def test_complete_extractor_namespace_exposes_canonical_contract() -> None:
    assert CompleteExtractorBase.__module__ == "scrapers.base.complete_extractor"
    assert (
        CompleteExtractorDomainConfig.__module__
        == "scrapers.base.complete_extractor"
    )


def test_legacy_complete_extractor_imports_remain_explicit_aliases() -> None:
    assert LegacyCompleteExtractorBase is CompleteExtractorBase
    assert LegacyCompleteExtractorDomainConfig is CompleteExtractorDomainConfig
