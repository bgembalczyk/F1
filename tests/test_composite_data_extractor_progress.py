from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.options import ScraperOptions
from scrapers.base.progress import NoOpProgressAdapter
from scrapers.composite_scraper import CompleteExtractorBase
from scrapers.composite_scraper import CompleteExtractorBaseChildren
from scrapers.source_adapter import IterableSourceAdapter

if TYPE_CHECKING:
    from collections.abc import Iterable


class SingleScraperStub:
    def extract_by_url(self, url: str) -> list[dict[str, str]]:
        return [{"fetched_from": url}]


class DemoCompositeExtractor(CompleteExtractorBase):
    url = "https://example.com"

    def build_children(self) -> CompleteExtractorBaseChildren:
        return CompleteExtractorBaseChildren(
            list_scraper=object(),
            single_scraper=SingleScraperStub(),
            records_adapter=IterableSourceAdapter(
                lambda: [
                    {"name": "A", "detail_url": "https://example.com/a"},
                    {"name": "B", "detail_url": "https://example.com/b"},
                ],
            ),
        )

    def get_detail_url(self, record: dict[str, Any]) -> str | None:
        return str(record.get("detail_url"))


class PassThroughProgress:
    def wrap(
        self,
        iterable: Iterable[dict[str, Any]],
        *,
        _desc: str,
        _unit: str,
    ) -> Iterable[dict[str, Any]]:
        return iterable


def test_composite_extractor_returns_same_records_with_default_and_noop_progress() -> (
    None
):
    options = ScraperOptions()

    default_progress_records = DemoCompositeExtractor(options=options).fetch()
    no_progress_records = DemoCompositeExtractor(
        options=options,
        progress=NoOpProgressAdapter(),
    ).fetch()

    assert default_progress_records == no_progress_records


def test_composite_extractor_accepts_injected_progress_strategy() -> None:
    options = ScraperOptions()
    extractor = DemoCompositeExtractor(
        options=options,
        progress=PassThroughProgress(),
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
