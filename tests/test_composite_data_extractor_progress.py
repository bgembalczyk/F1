from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from scrapers.base.composite_scraper import CompositeDataExtractor
from scrapers.base.composite_scraper import CompositeDataExtractorChildren
from scrapers.base.options import ScraperOptions
from scrapers.base.progress import NoOpProgressAdapter
from scrapers.base.source_adapter import IterableSourceAdapter


class _SingleScraperStub:
    def fetch_by_url(self, url: str) -> list[dict[str, str]]:
        return [{"fetched_from": url}]


class _DemoCompositeExtractor(CompositeDataExtractor):
    url = "https://example.com"

    def build_children(self) -> CompositeDataExtractorChildren:
        return CompositeDataExtractorChildren(
            list_scraper=object(),
            single_scraper=_SingleScraperStub(),
            records_adapter=IterableSourceAdapter(
                lambda: [
                    {"name": "A", "detail_url": "https://example.com/a"},
                    {"name": "B", "detail_url": "https://example.com/b"},
                ],
            ),
        )

    def get_detail_url(self, record: dict[str, Any]) -> str | None:
        return str(record.get("detail_url"))


class _PassThroughProgress:
    def wrap(
        self,
        iterable: Iterable[dict[str, Any]],
        *,
        desc: str,
        unit: str,
    ) -> Iterable[dict[str, Any]]:
        return iterable


def test_composite_extractor_returns_same_records_with_default_and_noop_progress() -> (
    None
):
    options = ScraperOptions()

    default_progress_records = _DemoCompositeExtractor(options=options).fetch()
    no_progress_records = _DemoCompositeExtractor(
        options=options,
        progress=NoOpProgressAdapter(),
    ).fetch()

    assert default_progress_records == no_progress_records


def test_composite_extractor_accepts_injected_progress_strategy() -> None:
    options = ScraperOptions()
    extractor = _DemoCompositeExtractor(
        options=options,
        progress=_PassThroughProgress(),
    )

    records = extractor.fetch()

    assert records == [
        {
            "name": "A",
            "detail_url": "https://example.com/a",
            "details": {"fetched_from": "https://example.com/a"},
        },
        {
            "name": "B",
            "detail_url": "https://example.com/b",
            "details": {"fetched_from": "https://example.com/b"},
        },
    ]
