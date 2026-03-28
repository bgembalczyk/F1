from __future__ import annotations

from typing import TYPE_CHECKING

from complete_extractor.base import CompleteExtractorBase
from complete_extractor.domain_config import CompleteExtractorDomainConfig
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
        list_scraper_clses=(_FakeListScraperA, _FakeListScraperB),
        single_scraper_cls=_FakeSingleScraper,
        detail_url_field_paths=("primary.url", "fallback_url"),
        filter_redlinks=True,
        record_assembler=_custom_record_assembler,
    )


def test_build_children_uses_configured_multiple_list_scrapers() -> None:
    extractor = _ConfiguredExtractor()

    assert isinstance(extractor.records_adapter, MultiIterableSourceAdapter)
    assert isinstance(extractor.list_scraper, list)
    assert len(extractor.list_scraper) == EXPECTED_LIST_SCRAPER_COUNT
    assert extractor.list_scraper[0].options.include_urls is True
    assert extractor.list_scraper[1].options.include_urls is True
    assert extractor.records_adapter.get() == [{"item": "a"}, {"item": "b"}]


def test_extract_detail_url_uses_fallbacks_and_ignores_redlinks() -> None:
    extractor = _ConfiguredExtractor()

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
    extractor = _ConfiguredExtractor()

    assert extractor.assemble_record(
        {"name": "Example"},
        {"url": "https://en.wikipedia.org/wiki/Example"},
    ) == {
        "record": {"name": "Example"},
        "detail_url": "https://en.wikipedia.org/wiki/Example",
    }
