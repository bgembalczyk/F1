from __future__ import annotations

import sys
from pathlib import Path
import types

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

if "bs4" not in sys.modules:
    bs4_stub = types.ModuleType("bs4")

    class _StubTag:
        def find_all(self, *_, **__):
            return []

        def find_all_next(self, *_, **__):
            return []

        def find(self, *_, **__):
            return None

        def get_text(self, *_, **__):
            return ""

    class _StubBeautifulSoup(_StubTag):
        def __init__(self, html: str, *_):
            self.html = html

    bs4_stub.Tag = _StubTag
    bs4_stub.BeautifulSoup = _StubBeautifulSoup
    sys.modules["bs4"] = bs4_stub

if "requests" not in sys.modules:
    requests_stub = types.ModuleType("requests")

    class _RequestException(Exception):
        pass

    class _Session:
        def get(self, *_args, **_kwargs):
            raise _RequestException("requests stub")

    requests_stub.RequestException = _RequestException
    requests_stub.Session = _Session
    sys.modules["requests"] = requests_stub

from scrapers.base.errors import ScraperNetworkError, ScraperParseError
from scrapers.base.list.scraper import F1ListScraper
from scrapers.base.scraper import F1Scraper
from scrapers.circuits.single_scraper import F1SingleCircuitScraper


class DummyFetcher:
    def __init__(self, *, html: str | None = None, exc: Exception | None = None) -> None:
        self.html = html
        self.exc = exc

    def get_text(self, url: str, *, timeout: int | None = None) -> str:
        if self.exc:
            raise self.exc
        assert self.html is not None
        return self.html


class DummyScraper(F1Scraper):
    url = "https://example.com"

    def _parse_soup(self, soup):
        return []


class DummyParseScraper(F1Scraper):
    url = "https://example.com"

    def _parse_soup(self, soup):
        raise ValueError("boom")


class DummyListScraper(F1ListScraper):
    url = "https://example.com"
    section_id = None
    record_key = "item"


def test_fetch_maps_network_errors_to_domain_exception():
    scraper = DummyScraper(fetcher=DummyFetcher(exc=RuntimeError("offline")))

    with pytest.raises(ScraperNetworkError):
        scraper.fetch()


def test_fetch_maps_parse_errors_to_domain_exception():
    scraper = DummyParseScraper(fetcher=DummyFetcher(html="<html></html>"))

    with pytest.raises(ScraperParseError):
        scraper.fetch()


def test_list_scraper_skips_missing_list_with_log():
    scraper = DummyListScraper(fetcher=DummyFetcher(html="<html></html>"))

    assert scraper.fetch() == []


def test_single_circuit_scraper_wraps_network_errors():
    scraper = F1SingleCircuitScraper(fetcher=DummyFetcher(exc=RuntimeError("offline")))

    with pytest.raises(ScraperNetworkError):
        scraper.fetch("https://example.com/wiki/Test")
