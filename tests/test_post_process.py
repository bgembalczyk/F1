from scrapers.base.ABC import F1Scraper
from scrapers.base.options import ScraperOptions


class DummySourceAdapter:
    def __init__(self, html: str) -> None:
        self.html = html

    def get(self, source: str | None = None, **_kwargs: object) -> str:
        return self.html


class FlagPostProcessor:
    def post_process(self, records):
        for record in records:
            record["flagged"] = True
        return records


class KeepOnlyPostProcessor:
    def post_process(self, records):
        return [record for record in records if record.get("keep")]


class DummyScraper(F1Scraper):
    url = "https://example.com"

    def _parse_soup(self, soup):
        return [
            {"keep": True, "value": 1},
            {"keep": False, "value": 2},
        ]


def test_post_processors_pipeline_applies_in_order():
    options = ScraperOptions(
        source_adapter=DummySourceAdapter("<html></html>"),
        post_processors=[FlagPostProcessor(), KeepOnlyPostProcessor()],
    )
    scraper = DummyScraper(options=options)

    records = scraper.fetch()

    assert records == [{"keep": True, "value": 1, "flagged": True}]
