from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from complete_extractor.base import CompleteExtractorBase
from complete_extractor.domain_config import CompleteExtractorDomainConfig
from infrastructure.http_client.requests_shim.request_error import RequestError
from scrapers.base.source_adapter import MultiIterableSourceAdapter

if TYPE_CHECKING:
    from scrapers.base.options import ScraperOptions


EXPECTED_LIST_SCRAPER_COUNT = 2


class FakeListScraperA:
    def __init__(self, *, options: ScraperOptions) -> None:
        self.options = options

    def fetch(self) -> list[dict[str, str]]:
        return [{"item": "a"}]


class FakeListScraperB:
    def __init__(self, *, options: ScraperOptions) -> None:
        self.options = options

    def fetch(self) -> list[dict[str, str]]:
        return [{"item": "b"}]


class FakeSingleScraper:
    def __init__(self, *, options: ScraperOptions) -> None:
        self.options = options

    def extract_by_url(self, url: str) -> list[dict[str, str]]:
        return [{"url": url}]


class FailingListScraper:
    def __init__(self, *, options: ScraperOptions) -> None:
        self.options = options

    def fetch(self) -> list[dict[str, str]]:
        msg = "programmer bug in list scraper"
        raise TypeError(msg)


class FailingSingleScraper:
    def __init__(self, *, options: ScraperOptions) -> None:
        self.options = options

    def extract_by_url(self, _url: str) -> list[dict[str, str]]:
        msg = "programmer bug in single scraper"
        raise TypeError(msg)


class DetailListScraper:
    def __init__(self, *, options: ScraperOptions) -> None:
        self.options = options

    def fetch(self) -> list[dict[str, str]]:
        return [{"fallback_url": "https://example.com/wiki/Item"}]


class RecoverableFailingSingleScraper:
    def __init__(self, *, options: ScraperOptions) -> None:
        self.options = options

    def extract_by_url(self, _url: str) -> list[dict[str, str]]:
        msg = "temporary offline"
        raise RequestError(msg)


def custom_record_assembler(
    record: dict[str, object],
    details: dict[str, object] | None,
) -> dict[str, object]:
    return {
        "record": record,
        "detail_url": details.get("url") if isinstance(details, dict) else None,
    }


class ConfiguredExtractor(CompleteExtractorBase):
    url = "https://example.com"
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_classes=(FakeListScraperA, FakeListScraperB),
        single_scraper_cls=FakeSingleScraper,
        detail_url_field_paths=("primary.url", "fallback_url"),
        filter_redlinks=True,
        record_assembler=custom_record_assembler,
    )


class ProgrammerListErrorExtractor(CompleteExtractorBase):
    url = "https://example.com"
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_classes=(FailingListScraper,),
        single_scraper_cls=FakeSingleScraper,
        detail_url_field_paths=("fallback_url",),
    )


class ProgrammerSingleErrorExtractor(CompleteExtractorBase):
    url = "https://example.com"
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_classes=(DetailListScraper,),
        single_scraper_cls=FailingSingleScraper,
        detail_url_field_paths=("fallback_url",),
    )


class RecoverableSingleErrorExtractor(CompleteExtractorBase):
    url = "https://example.com"
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_classes=(FakeListScraperA,),
        single_scraper_cls=RecoverableFailingSingleScraper,
        detail_url_field_paths=("fallback_url",),
    )


def test_build_children_uses_configured_multiple_list_scrapers() -> None:
    extractor = ConfiguredExtractor()

    assert isinstance(extractor.records_adapter, MultiIterableSourceAdapter)
    assert isinstance(extractor.list_scraper, list)
    assert len(extractor.list_scraper) == EXPECTED_LIST_SCRAPER_COUNT
    assert extractor.list_scraper[0].options.include_urls is True
    assert extractor.list_scraper[1].options.include_urls is True
    assert extractor.records_adapter.get() == [{"item": "a"}, {"item": "b"}]


def test_extract_detail_url_uses_fallbacks_and_ignores_redlinks() -> None:
    extractor = ConfiguredExtractor()

    assert (
        extractor.extract_detail_url(
            {
                "primary": {
                    "url": "https://en.wikipedia.org/w/index.php?title=Missing&action=edit&redlink=1",
                },
                "fallback_url": "https://en.wikipedia.org/wiki/Real_page",
            },
        )
        == "https://en.wikipedia.org/wiki/Real_page"
    )


def test_assemble_record_uses_custom_assembler() -> None:
    extractor = ConfiguredExtractor()

    assert extractor.assemble_record(
        {"name": "Example"},
        {"url": "https://en.wikipedia.org/wiki/Example"},
    ) == {
        "record": {"name": "Example"},
        "detail_url": "https://en.wikipedia.org/wiki/Example",
    }


@pytest.mark.parametrize(
    "legacy_field, value",
    [
        ("list_scraper_cls", FakeListScraperA),
        ("list_scraper_clses", (FakeListScraperA, FakeListScraperB)),
        ("detail_url_field_path", "primary.url"),
    ],
)
def test_config_rejects_legacy_fields(legacy_field: str, value: object) -> None:
    with pytest.raises(TypeError, match=legacy_field):
        CompleteExtractorDomainConfig(
            list_scraper_classes=(FakeListScraperA,),
            single_scraper_cls=FakeSingleScraper,
            detail_url_field_paths=("fallback_url",),
            **{legacy_field: value},
        )


def test_fetch_propagates_programmer_error_from_list_scraper() -> None:
    extractor = ProgrammerListErrorExtractor()

    with pytest.raises(TypeError, match="programmer bug in list scraper"):
        extractor.fetch()


def test_fetch_propagates_programmer_error_from_single_scraper() -> None:
    extractor = ProgrammerSingleErrorExtractor()

    with pytest.raises(TypeError, match="programmer bug in single scraper"):
        extractor.fetch()


def test_fetch_soft_skips_recoverable_single_scraper_errors() -> None:
    extractor = RecoverableSingleErrorExtractor()
    result = extractor.fetch()

    assert result == [{"item": "a", "details": None}]
