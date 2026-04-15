# ruff: noqa: ARG002, ARG005, EM101, N801, SLF001, TRY003
from types import SimpleNamespace
from unittest.mock import patch

from scrapers.scraper_table import F1TableScraper
from scrapers.seed_list_scraper_table import SeedListTableScraper


def _make_scraper(section_id="Section"):
    """Build a minimal SeedListTableScraper instance bypassing full init."""
    scraper = object.__new__(SeedListTableScraper)
    scraper.config = SimpleNamespace(section_id=section_id)
    scraper.include_urls = False
    scraper.normalize_empty_values = True
    return scraper


def test_parse_section_or_fallback_uses_legacy_flow_when_no_section_id():
    scraper = _make_scraper(section_id=None)

    with patch.object(F1TableScraper, "_parse_soup", return_value=["fallback"]):
        records = scraper.parse_section_or_fallback(
            object(),
            domain="circuits",
            parser_factory=lambda: object(),
        )

    assert records == ["fallback"]


class _DeclarativeScraper(SeedListTableScraper):
    domain = "constructors"
    section_label = "Current constructors"

    class section_parser_class:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def parse(self, _fragment):
            class _Result:
                records = ["parsed"]

            return _Result()
