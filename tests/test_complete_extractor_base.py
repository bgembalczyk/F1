from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from complete_extractor.base import CompleteExtractorBase
from complete_extractor.domain_config import CompleteExtractorDomainConfig
from infrastructure.http_client.requests_shim.request_error import RequestError
from scrapers.base.composite_dto import ListRecordDTO
from scrapers.base.source_adapter import MultiIterableSourceAdapter

if TYPE_CHECKING:
    from scrapers.base.options import ScraperOptions


EXPECTED_LIST_SCRAPER_COUNT = 2


class _FakeListScraperA:
    def __init__(self, *, options: ScraperOptions) -> None:
        self.options = options

    def fetch(self) -> list[dict[str, str]]:
        return [{"item": "a"}]


class _FakeListScraperB:
    def __init__(self, *, options: ScraperOptions) -> None:
        self.options = options

    def fetch(self) -> list[dict[str, str]]:
        return [{"item": "b"}]


class _FakeSingleScraper:
    def __init__(self, *, options: ScraperOptions) -> None:
        self.options = options

    def fetch_by_url(self, url: str) -> list[dict[str, str]]:
        return [{"url": url}]


class _FailingListScraper:
    def __init__(self, *, options: ScraperOptions) -> None:
        self.options = options

    def fetch(self) -> list[dict[str, str]]:
        raise TypeError("programmer bug in list scraper")


class _FailingSingleScraper:
    def __init__(self, *, options: ScraperOptions) -> None:
        self.options = options

    def fetch_by_url(self, _url: str) -> list[dict[str, str]]:
        raise TypeError("programmer bug in single scraper")


class _DetailListScraper:
    def __init__(self, *, options: ScraperOptions) -> None:
        self.options = options

    def fetch(self) -> list[dict[str, str]]:
        return [{"fallback_url": "https://example.com/wiki/Item"}]


class _RecoverableFailingSingleScraper:
    def __init__(self, *, options: ScraperOptions) -> None:
        self.options = options

    def fetch_by_url(self, _url: str) -> list[dict[str, str]]:
        raise RequestError("temporary offline")


def _custom_record_assembler(
    record: dict[str, object],
    details: dict[str, object] | None,
) -> dict[str, object]:
    return {
        "record": record,
        "detail_url": details.get("url") if isinstance(details, dict) else None,
    }


class _ConfiguredExtractor(CompleteExtractorBase):
    url = "https://example.com"
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_classes=(_FakeListScraperA, _FakeListScraperB),
        single_scraper_cls=_FakeSingleScraper,
        detail_url_field_paths=("primary.url", "fallback_url"),
        filter_redlinks=True,
        record_assembler=_custom_record_assembler,
    )


class _LegacySingleListExtractor(CompleteExtractorBase):
    url = "https://example.com"
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_cls=_FakeListScraperA,
        single_scraper_cls=_FakeSingleScraper,
        detail_url_field_path="primary.url",
    )


class _LegacyMultiListExtractor(CompleteExtractorBase):
    url = "https://example.com"
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_clses=(_FakeListScraperA, _FakeListScraperB),
        single_scraper_cls=_FakeSingleScraper,
        detail_url_field_paths=("fallback_url",),
        detail_url_field_path="primary.url",
    )


class _ProgrammerListErrorExtractor(CompleteExtractorBase):
    url = "https://example.com"
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_classes=(_FailingListScraper,),
        single_scraper_cls=_FakeSingleScraper,
        detail_url_field_paths=("fallback_url",),
    )


class _ProgrammerSingleErrorExtractor(CompleteExtractorBase):
    url = "https://example.com"
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_classes=(_DetailListScraper,),
        single_scraper_cls=_FailingSingleScraper,
        detail_url_field_paths=("fallback_url",),
    )


class _RecoverableSingleErrorExtractor(CompleteExtractorBase):
    url = "https://example.com"
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_classes=(_FakeListScraperA,),
        single_scraper_cls=_RecoverableFailingSingleScraper,
        detail_url_field_paths=("fallback_url",),
    )


def test_build_children_uses_configured_multiple_list_scrapers() -> None:
    extractor = _ConfiguredExtractor()

    assert isinstance(extractor.records_adapter, MultiIterableSourceAdapter)
    assert isinstance(extractor.list_scraper, list)
    assert len(extractor.list_scraper) == EXPECTED_LIST_SCRAPER_COUNT
    assert extractor.list_scraper[0].options.include_urls is True
    assert extractor.list_scraper[1].options.include_urls is True
    assert extractor.records_adapter.get() == [
        ListRecordDTO.from_dict({"item": "a"}),
        ListRecordDTO.from_dict({"item": "b"}),
    ]


def test_extract_detail_url_uses_fallbacks_and_ignores_redlinks() -> None:
    extractor = _ConfiguredExtractor()

    assert (
        extractor.extract_detail_url(
            ListRecordDTO.from_dict(
                {
                    "primary": {
                        "url": "https://en.wikipedia.org/w/index.php?title=Missing&action=edit&redlink=1",
                    },
                    "fallback_url": "https://en.wikipedia.org/wiki/Real_page",
                },
            ),
        )
        == "https://en.wikipedia.org/wiki/Real_page"
    )


def test_assemble_record_uses_custom_assembler() -> None:
    extractor = _ConfiguredExtractor()

    assembled = extractor.assemble_record(
        ListRecordDTO.from_dict({"name": "Example"}),
        extractor.json_boundary.detail_from_json(
            {"url": "https://en.wikipedia.org/wiki/Example"},
        ),
    )

    assert assembled.to_dict() == {
        "record": {"name": "Example"},
        "detail_url": "https://en.wikipedia.org/wiki/Example",
    }


def test_config_normalization_supports_legacy_single_list_fields() -> None:
    extractor = _LegacySingleListExtractor()

    assert extractor.DOMAIN_CONFIG.list_scraper_classes == (_FakeListScraperA,)
    assert extractor.DOMAIN_CONFIG.detail_url_field_paths == ("primary.url",)
    assert extractor.records_adapter.get() == [ListRecordDTO.from_dict({"item": "a"})]


def test_config_normalization_supports_legacy_multi_list_fields() -> None:
    extractor = _LegacyMultiListExtractor()

    assert extractor.DOMAIN_CONFIG.list_scraper_classes == (
        _FakeListScraperA,
        _FakeListScraperB,
    )
    assert extractor.DOMAIN_CONFIG.detail_url_field_paths == (
        "primary.url",
        "fallback_url",
    )
    assert isinstance(extractor.records_adapter, MultiIterableSourceAdapter)
    assert extractor.records_adapter.get() == [
        ListRecordDTO.from_dict({"item": "a"}),
        ListRecordDTO.from_dict({"item": "b"}),
    ]


def test_fetch_propagates_programmer_error_from_list_scraper() -> None:
    extractor = _ProgrammerListErrorExtractor()

    with pytest.raises(TypeError, match="programmer bug in list scraper"):
        extractor.fetch()


def test_fetch_propagates_programmer_error_from_single_scraper() -> None:
    extractor = _ProgrammerSingleErrorExtractor()

    with pytest.raises(TypeError, match="programmer bug in single scraper"):
        extractor.fetch()


def test_fetch_soft_skips_recoverable_single_scraper_errors() -> None:
    extractor = _RecoverableSingleErrorExtractor()
    result = extractor.fetch()

    assert result == [{"item": "a", "details": None}]
