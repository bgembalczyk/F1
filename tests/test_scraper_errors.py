import json
import sys
import types
from pathlib import Path

import pytest

from infrastructure.http_client.requests_shim.request_error import RequestError
from scrapers.base.abc import ABCScraper
from scrapers.base.error_handler import ErrorHandler
from scrapers.base.errors import DomainParseError
from scrapers.base.errors import ScraperNetworkError
from scrapers.base.errors import ScraperNotFoundError
from scrapers.base.errors import ScraperParseError
from scrapers.base.errors_report import ErrorReport
from scrapers.base.errors_report import write_error_report
from scrapers.base.errors_report import write_error_summary_by_code
from scrapers.base.infobox.scraper import WikipediaInfoboxScraper
from scrapers.base.list.scraper import F1ListScraper
from scrapers.base.options import ScraperOptions
from scrapers.circuits.infobox.services.additional_info import (
    CircuitAdditionalInfoParser,
)
from scrapers.circuits.infobox.services.entities import CircuitEntitiesParser
from scrapers.circuits.infobox.services.entity_parsing import CircuitEntityParser
from scrapers.circuits.infobox.services.geo import CircuitGeoParser
from scrapers.circuits.infobox.services.history import CircuitHistoryParser
from scrapers.circuits.infobox.services.lap_record import CircuitLapRecordParser
from scrapers.circuits.infobox.services.specs import CircuitSpecsParser
from scrapers.circuits.infobox.services.text_utils import InfoboxTextUtils
from scrapers.circuits.single_scraper import F1SingleCircuitScraper
from scrapers.grands_prix.single_scraper import F1SingleGrandPrixScraper

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

        def select(self, *_, **__):
            return []

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

    class _RequestError(Exception):
        pass

    class _Session:
        def get(self, *_args, **_kwargs):
            msg = "requests stub"
            raise _RequestError(msg)

    requests_stub.RequestException = _RequestError
    requests_stub.Session = _Session
    sys.modules["requests"] = requests_stub

if "certifi" not in sys.modules:
    certifi_stub = types.ModuleType("certifi")

    def _where():
        return ""

    certifi_stub.where = _where
    sys.modules["certifi"] = certifi_stub

if "pandas" not in sys.modules:
    pandas_stub = types.ModuleType("pandas")

    class _StubDataFrame:
        def __init__(self, *_args, **_kwargs):
            pass

    pandas_stub.DataFrame = _StubDataFrame
    sys.modules["pandas"] = pandas_stub


class DummyFetcher:
    def __init__(
        self,
        *,
        html: str | None = None,
        exc: Exception | None = None,
    ) -> None:
        self.html = html
        self.exc = exc

    def get_text(self, _url: str, *, _timeout: int | None = None) -> str:
        if self.exc:
            raise self.exc
        assert self.html is not None
        return self.html

    def get(self, _url: str) -> str:
        return self.get_text(_url)


class DummyScraper(ABCScraper):
    url = "https://example.com"

    def _parse_soup(self, _soup):
        return []


class DummyParseScraper(ABCScraper):
    url = "https://example.com"

    def _parse_soup(self, _soup):
        msg = "boom"
        raise ValueError(msg)


class DummyTypeErrorScraper(ABCScraper):
    url = "https://example.com"

    def _parse_soup(self, _soup):
        msg = "type boom"
        raise TypeError(msg)


class DummyListScraper(F1ListScraper):
    url = "https://example.com"
    section_id = None
    record_key = "item"


class DummyInfoboxParser:
    def parse(self, _soup):
        msg = "Brak infoboksu"
        raise ScraperNotFoundError(msg)


class DummySingleCircuitScraper(F1SingleCircuitScraper):
    def _is_circuit_like_article(self, _soup) -> bool:
        return True

    def _parse_details(self, _soup):
        msg = "Brak danych"
        raise ScraperNotFoundError(msg)


class FlakyRequestFetcher:
    def __init__(self, *, html: str, failures: int) -> None:
        self.html = html
        self.failures = failures
        self.calls = 0

    def get_text(self, _url: str, *, _timeout: int | None = None) -> str:
        self.calls += 1
        if self.calls <= self.failures:
            raise RequestError("temporary offline")
        return self.html

    def get(self, _url: str) -> str:
        return self.get_text(_url)


def test_scraper_error_contract_is_consistent() -> None:
    cause = ValueError("boom")

    error = DomainParseError(
        "Brak sekcji",
        url="https://example.com/wiki/Test",
        cause=cause,
    )

    assert error.message == "Brak sekcji"
    assert error.url == "https://example.com/wiki/Test"
    assert error.cause is cause
    assert error.critical is False
    assert error.args == ("Brak sekcji",)


def test_fetch_maps_network_errors_to_domain_exception():
    scraper = DummyScraper(
        options=ScraperOptions(fetcher=DummyFetcher(exc=RuntimeError("offline"))),
    )

    with pytest.raises(ScraperNetworkError):
        scraper.fetch()


def test_fetch_maps_parse_errors_to_domain_exception():
    scraper = DummyParseScraper(
        options=ScraperOptions(fetcher=DummyFetcher(html="<html></html>")),
    )

    with pytest.raises(ScraperParseError):
        scraper.fetch()


def test_fetch_propagates_type_error_as_non_recoverable() -> None:
    scraper = DummyTypeErrorScraper(
        options=ScraperOptions(fetcher=DummyFetcher(html="<html></html>")),
    )

    with pytest.raises(TypeError):
        scraper.fetch()


def test_fetch_retry_policy_retries_recoverable_network_error() -> None:
    fetcher = FlakyRequestFetcher(html="<html></html>", failures=1)
    scraper = DummyScraper(
        options=ScraperOptions(
            fetcher=fetcher,
            error_policy="retry",
            error_retry_attempts=2,
        ),
    )

    assert scraper.fetch() == []
    assert fetcher.calls == 2


def test_fetch_skip_policy_soft_skips_recoverable_network_error() -> None:
    fetcher = FlakyRequestFetcher(html="<html></html>", failures=2)
    scraper = DummyScraper(
        options=ScraperOptions(
            fetcher=fetcher,
            error_policy="skip",
        ),
    )

    assert scraper.fetch() == []


def test_list_scraper_skips_missing_list_with_log():
    scraper = DummyListScraper(
        options=ScraperOptions(fetcher=DummyFetcher(html="<html></html>")),
    )

    assert scraper.fetch() == []


def test_single_circuit_scraper_wraps_network_errors():
    scraper = F1SingleCircuitScraper(
        options=ScraperOptions(fetcher=DummyFetcher(exc=RuntimeError("offline"))),
    )

    with pytest.raises(ScraperNetworkError):
        scraper.fetch_by_url("https://example.com/wiki/Test")


def test_error_report_contains_catalog_code_fields() -> None:
    error = ScraperParseError(
        message="Parse failed",
        url="https://example.com",
        parser_name="DummyParser",
        run_id="run-1",
    )
    report = ErrorReport.from_exception(error)

    assert report.code == "source.parse_error"
    assert report.code_id == "P001"
    assert report.code_description


def test_error_summary_aggregates_entries_by_code(tmp_path: Path) -> None:
    report_path = tmp_path / "errors.jsonl"
    write_error_report(
        tmp_path,
        ErrorReport.from_exception(
            ScraperParseError(message="parse"),
            run_id="run-a",
        ),
    )
    write_error_report(
        tmp_path,
        ErrorReport.from_exception(
            ScraperNetworkError(message="net"),
            run_id="run-a",
        ),
    )
    write_error_report(
        tmp_path,
        ErrorReport.from_exception(
            ScraperParseError(message="parse2"),
            run_id="run-b",
        ),
    )

    assert report_path.exists()

    summary_path = write_error_summary_by_code(tmp_path, run_id="run-a")
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["total_errors"] == 2
    assert payload["error_counts_by_code"] == {"M002": 1, "P001": 1}


def test_single_circuit_scraper_soft_skips_not_found():
    scraper = DummySingleCircuitScraper(
        options=ScraperOptions(fetcher=DummyFetcher(html="<html></html>")),
    )

    assert scraper.fetch_by_url("https://example.com/wiki/Test") == []


def test_infobox_scraper_soft_skips_not_found():
    scraper = WikipediaInfoboxScraper(
        fetcher=DummyFetcher(html="<html></html>"),
        parser=DummyInfoboxParser(),
    )

    assert scraper.scrape("https://example.com/wiki/Test") == {}


def test_single_grand_prix_scraper_soft_skips_missing_section(monkeypatch):
    monkeypatch.setattr(
        "scrapers.grands_prix.single_scraper.is_grand_prix_article",
        lambda _soup: True,
    )
    scraper = F1SingleGrandPrixScraper(
        options=ScraperOptions(fetcher=DummyFetcher(html="<html></html>")),
    )

    result = scraper.fetch_by_url("https://example.com/wiki/Test")

    assert result == [{"url": scraper.url, "by_year": None}]


def test_circuit_entities_parser_skips_domain_parse_errors():
    handler = ErrorHandler()
    parser = CircuitEntitiesParser(
        text_utils=InfoboxTextUtils(),
        geo_parser=CircuitGeoParser(),
        history_parser=CircuitHistoryParser(),
        specs_parser=CircuitSpecsParser(),
        lap_record_parser=CircuitLapRecordParser(),
        entity_parser=CircuitEntityParser(),
        additional_info_parser=CircuitAdditionalInfoParser(),
        error_handler=handler,
        url_provider=lambda: "https://example.com/wiki/Test",
    )

    raw = {
        "title": "Test Circuit",
        "rows": {
            "length": {"text": "not-a-number", "links": []},
        },
    }

    result = parser.with_normalized(raw, [])

    assert result["normalized"]["name"] == "Test Circuit"
    assert result["normalized"].get("specs") is None
