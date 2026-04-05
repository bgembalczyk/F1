import logging
import sys
import types
from pathlib import Path
from typing import Any

import pytest
from bs4 import BeautifulSoup

from scrapers.base.abc import ABCScraper
from scrapers.base.options import ScraperOptions
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.circuits.single_scraper import F1SingleCircuitScraper
from scrapers.constructors.constructors_list import ConstructorsListScraper
from tests.support.dependency_stubs import ensure_optional_deps

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

ensure_optional_deps(
    require_bs4=True,
    bs4_skip_reason="bs4 is required for scraper contract tests",
)

try:
    import scrapers.base.infobox.circuits.scraper  # noqa: F401
except ImportError:
    infobox_stub = types.ModuleType("scrapers.base.infobox.circuits.scraper")

    class _StubF1CircuitInfoboxScraper:
        def __init__(self, *_, **__):
            pass

        def parse(self, _soup):
            return {}

    infobox_stub.F1CircuitInfoboxScraper = _StubF1CircuitInfoboxScraper
    sys.modules["scrapers.base.infobox.circuits.scraper"] = infobox_stub


class StubFetcher:
    def __init__(self, html: str) -> None:
        self.html = html
        self.calls = 0

    def get_text(self, _url: str, *, _timeout: int | None = None) -> str:
        self.calls += 1
        return self.html

    def get(self, _url: str) -> str:
        return self.get_text(_url)


class DummyTableScraper(F1TableScraper):
    def _parse_soup(self, _soup):
        return []


class DummySourceAdapter:
    def __init__(self, html: str) -> None:
        self.html = html

    def get(self, _url: str) -> str:
        return self.html


class DummyScraper(ABCScraper):
    url = "https://example.com"

    def _parse_soup(self, _soup: BeautifulSoup) -> list[dict[str, Any]]:
        return [{"id": 1}]


class DummyFetcher:
    def __init__(self, html: str) -> None:
        self.html = html

    def get_text(self, _url: str, *, _timeout: int | None = None) -> str:
        return self.html

    def get(self, _url: str) -> str:
        return self.get_text(_url)


class DummySingleCircuitScraper(F1SingleCircuitScraper):
    def __init__(self, *, is_circuit: bool, details: dict[str, Any] | None) -> None:
        super().__init__(options=ScraperOptions(fetcher=DummyFetcher("")))
        self._is_circuit = is_circuit
        self._details = details

    def _is_circuit_like_article(self, _soup: BeautifulSoup) -> bool:
        return self._is_circuit

    def _parse_details(self, _soup: BeautifulSoup) -> dict[str, Any]:
        return self._details or {}


def test_scraper_propagates_parsing_errors() -> None:
    class _ErrorScraper(ABCScraper):
        url = "https://example.com"

        def _parse_soup(self, _soup: BeautifulSoup) -> list[dict[str, Any]]:
            raise RuntimeError("parsing failed")

    scraper = _ErrorScraper(
        options=ScraperOptions(fetcher=StubFetcher("<html></html>")),
    )

    with pytest.raises(RuntimeError, match="parsing failed"):
        scraper.get_data()


def test_table_scraper_returns_dict_records() -> None:
    html = """
    <html>
      <body>
        <h2><span id="Circuits">Circuits</span></h2>
        <table class="wikitable">
          <tr>
            <th>Circuit</th>
            <th>Type</th>
            <th>Location</th>
            <th>Country</th>
          </tr>
          <tr>
            <td><a href="/wiki/Test_Circuit">Test Circuit</a></td>
            <td>Street</td>
            <td>Test City</td>
            <td>Testland</td>
          </tr>
        </table>
      </body>
    </html>
    """

    scraper = CircuitsListScraper(
        options=ScraperOptions(fetcher=StubFetcher(html), include_urls=True),
    )
    data = scraper.get_data()

    assert data
    assert all(isinstance(record, dict) for record in data)


def test_scraper_sets_logger_adapter() -> None:
    scraper = CircuitsListScraper(
        options=ScraperOptions(fetcher=StubFetcher("<html></html>")),
    )

    assert scraper.logger is not None
    assert isinstance(scraper.logger, logging.LoggerAdapter)
    assert scraper.logger.extra.get("scraper") == scraper.__class__.__name__


def test_scraper_config_rejects_blank_url() -> None:
    with pytest.raises(ValueError, match="url must be a non-empty string"):
        ScraperConfig(url=" ")


def test_scraper_config_rejects_invalid_column_map() -> None:
    with pytest.raises(TypeError, match="column_map must map str keys to str values"):
        ScraperConfig(
            url="https://example.com",
            column_map={"Header": 123},
        )


def test_scraper_config_rejects_invalid_columns() -> None:
    with pytest.raises(
        TypeError,
        match="columns must map str keys to BaseColumn values",
    ):
        ScraperConfig(
            url="https://example.com",
            columns={"Header": "not-a-column"},
        )


def test_table_scraper_validates_config_in_init() -> None:
    config = object.__new__(ScraperConfig)
    object.__setattr__(config, "url", "https://example.com")
    object.__setattr__(config, "section_id", None)
    object.__setattr__(config, "expected_headers", None)
    object.__setattr__(config, "column_map", {})
    object.__setattr__(config, "columns", {"Header": "not-a-column"})
    object.__setattr__(config, "table_css_class", "wikitable")
    object.__setattr__(config, "model_class", None)
    object.__setattr__(config, "default_column", AutoColumn())

    with pytest.raises(
        TypeError,
        match="columns must map str keys to BaseColumn values",
    ):
        DummyTableScraper(
            options=ScraperOptions(fetcher=StubFetcher("<html></html>")),
            config=config,
        )


def test_f1scraper_fetch_always_returns_list() -> None:
    scraper = DummyScraper(
        options=ScraperOptions(source_adapter=DummySourceAdapter("<html></html>")),
    )

    result = scraper.fetch()

    assert isinstance(result, list)
    assert result == [{"id": 1}]


def test_single_scraper_returns_single_item_list() -> None:
    scraper = DummySingleCircuitScraper(
        is_circuit=True,
        details={"infobox": {"name": "Test"}, "tables": []},
    )

    result = scraper.extract_by_url("https://example.com/wiki/Test")

    assert len(result) == 1
    assert result[0]["url"] == "https://example.com/wiki/Test"
    assert result[0]["infobox"]["name"] == "Test"


def test_single_scraper_returns_empty_list_when_not_circuit() -> None:
    scraper = DummySingleCircuitScraper(is_circuit=False, details=None)

    result = scraper.extract_by_url("https://example.com/wiki/Test")

    assert result == []
