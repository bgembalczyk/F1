import importlib.util
import logging
import sys
from pathlib import Path
import types
from typing import Any, Dict, List
import pytest
from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.base.scraper import F1Scraper
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.constructors.privateer_teams_list import PrivateerTeamsListScraper
from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.circuits.single_scraper import F1SingleCircuitScraper

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

if importlib.util.find_spec("requests") is None:
    requests_stub = types.ModuleType("requests")

    class _RequestException(Exception):
        pass

    class _Session:
        def get(self, *_args, **_kwargs):
            raise _RequestException("requests stub")

    requests_stub.RequestException = _RequestException
    requests_stub.Session = _Session
    sys.modules["requests"] = requests_stub

if importlib.util.find_spec("certifi") is None:
    certifi_stub = types.ModuleType("certifi")

    def _where():
        return ""

    certifi_stub.where = _where
    sys.modules["certifi"] = certifi_stub

if importlib.util.find_spec("pandas") is None:
    pandas_stub = types.ModuleType("pandas")

    class _StubDataFrame:
        def __init__(self, *_args, **_kwargs):
            pass

    pandas_stub.DataFrame = _StubDataFrame
    sys.modules["pandas"] = pandas_stub

if importlib.util.find_spec("bs4") is None:
    pytest.skip("bs4 is required for scraper contract tests", allow_module_level=True)


try:
    import scrapers.base.infobox.circuits.scraper  # noqa: F401
except Exception:
    infobox_stub = types.ModuleType("scrapers.base.infobox.circuits.scraper")

    class _StubF1CircuitInfoboxScraper:
        def __init__(self, *_, **__):
            pass

        def parse(self, soup):
            return {}

    infobox_stub.F1CircuitInfoboxScraper = _StubF1CircuitInfoboxScraper
    sys.modules["scrapers.base.infobox.circuits.scraper"] = infobox_stub


class StubFetcher:
    def __init__(self, html: str) -> None:
        self.html = html
        self.calls = 0

    def get_text(self, url: str, *, timeout: int | None = None) -> str:
        self.calls += 1
        return self.html

    def get(self, url: str) -> str:
        return self.get_text(url)


class DummyTableScraper(F1TableScraper):
    def _parse_soup(self, soup):
        return []


class DummySourceAdapter:
    def __init__(self, html: str) -> None:
        self.html = html

    def get(self, url: str) -> str:
        return self.html


class DummyScraper(F1Scraper):
    url = "https://example.com"

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return [{"id": 1}]


class DummyFetcher:
    def __init__(self, html: str) -> None:
        self.html = html

    def get_text(self, url: str, *, timeout: int | None = None) -> str:
        return self.html

    def get(self, url: str) -> str:
        return self.get_text(url)


class DummySingleCircuitScraper(F1SingleCircuitScraper):
    def __init__(self, *, is_circuit: bool, details: Dict[str, Any] | None) -> None:
        super().__init__(options=ScraperOptions(fetcher=DummyFetcher("")))
        self._is_circuit = is_circuit
        self._details = details

    def _is_circuit_like_article(self, soup: BeautifulSoup) -> bool:
        return self._is_circuit

    def _parse_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        return self._details or {}


def test_privateer_scraper_contract_builds_consistent_result() -> None:
    html = """
    <html>
      <body>
        <h2><span id="Privateer_teams">Privateer teams</span></h2>
        <ul>
          <li>
            <span class="flagicon">flag</span>
            <a href="/wiki/BMS_Scuderia_Italia">BMS Scuderia Italia</a> (1988–1993)
          </li>
          <li>
            <a href="/wiki/Tyrrell_Racing">Tyrrell</a> (1970, 1973–1974)
          </li>
        </ul>
      </body>
    </html>
    """

    fetcher = StubFetcher(html)
    scraper = PrivateerTeamsListScraper(
        options=ScraperOptions(fetcher=fetcher, include_urls=True)
    )

    data = scraper.get_data()
    assert fetcher.calls == 1

    assert data == [
        {
            "team": "BMS Scuderia Italia",
            "team_url": "https://en.wikipedia.org/wiki/BMS_Scuderia_Italia",
            "seasons": [
                {
                    "year": 1988,
                    "url": "https://en.wikipedia.org/wiki/1988_Formula_One_World_Championship",
                },
                {
                    "year": 1989,
                    "url": "https://en.wikipedia.org/wiki/1989_Formula_One_World_Championship",
                },
                {
                    "year": 1990,
                    "url": "https://en.wikipedia.org/wiki/1990_Formula_One_World_Championship",
                },
                {
                    "year": 1991,
                    "url": "https://en.wikipedia.org/wiki/1991_Formula_One_World_Championship",
                },
                {
                    "year": 1992,
                    "url": "https://en.wikipedia.org/wiki/1992_Formula_One_World_Championship",
                },
                {
                    "year": 1993,
                    "url": "https://en.wikipedia.org/wiki/1993_Formula_One_World_Championship",
                },
            ],
        },
        {
            "team": "Tyrrell",
            "team_url": "https://en.wikipedia.org/wiki/Tyrrell_Racing",
            "seasons": [
                {
                    "year": 1970,
                    "url": "https://en.wikipedia.org/wiki/1970_Formula_One_World_Championship",
                },
                {
                    "year": 1973,
                    "url": "https://en.wikipedia.org/wiki/1973_Formula_One_World_Championship",
                },
                {
                    "year": 1974,
                    "url": "https://en.wikipedia.org/wiki/1974_Formula_One_World_Championship",
                },
            ],
        },
    ]

    result = scraper.build_result(data=data)
    assert result.data is data
    assert result.source_url == scraper.url

    same_data = scraper.get_data()
    assert same_data == data
    assert fetcher.calls == 1


def test_scraper_propagates_parsing_errors() -> None:
    html = """
    <html>
      <body>
        <h2><span id="Other">Other</span></h2>
        <ul><li>No matching section</li></ul>
      </body>
    </html>
    """

    scraper = PrivateerTeamsListScraper(
        options=ScraperOptions(fetcher=StubFetcher(html))
    )

    with pytest.raises(RuntimeError, match="Nie znaleziono sekcji"):
        scraper.get_data()


def test_list_scraper_returns_dict_records() -> None:
    html = """
    <html>
      <body>
        <h2><span id="Privateer_teams">Privateer teams</span></h2>
        <ul>
          <li>
            <a href="/wiki/Tyrrell_Racing">Tyrrell</a> (1970)
          </li>
        </ul>
      </body>
    </html>
    """

    scraper = PrivateerTeamsListScraper(
        options=ScraperOptions(fetcher=StubFetcher(html), include_urls=True)
    )
    data = scraper.get_data()

    assert data
    assert all(isinstance(record, dict) for record in data)


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
        options=ScraperOptions(fetcher=StubFetcher(html), include_urls=True)
    )
    data = scraper.get_data()

    assert data
    assert all(isinstance(record, dict) for record in data)


def test_scraper_sets_logger_adapter() -> None:
    scraper = PrivateerTeamsListScraper(
        options=ScraperOptions(fetcher=StubFetcher("<html></html>"))
    )

    assert scraper.logger is not None
    assert isinstance(scraper.logger, logging.LoggerAdapter)
    assert scraper.logger.extra.get("scraper") == scraper.__class__.__name__


def test_scraper_config_rejects_blank_url() -> None:
    with pytest.raises(ValueError, match="url must be a non-empty string"):
        ScraperConfig(url=" ")


def test_scraper_config_rejects_invalid_column_map() -> None:
    with pytest.raises(ValueError, match="column_map must map str keys to str values"):
        ScraperConfig(
            url="https://example.com",
            column_map={"Header": 123},
        )


def test_scraper_config_rejects_invalid_columns() -> None:
    with pytest.raises(
        ValueError, match="columns must map str keys to BaseColumn values"
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
        ValueError, match="columns must map str keys to BaseColumn values"
    ):
        DummyTableScraper(
            options=ScraperOptions(fetcher=StubFetcher("<html></html>")),
            config=config,
        )


def test_f1scraper_fetch_always_returns_list() -> None:
    scraper = DummyScraper(
        options=ScraperOptions(source_adapter=DummySourceAdapter("<html></html>"))
    )

    result = scraper.fetch()

    assert isinstance(result, list)
    assert result == [{"id": 1}]


def test_single_scraper_returns_single_item_list() -> None:
    scraper = DummySingleCircuitScraper(
        is_circuit=True, details={"infobox": {"name": "Test"}, "tables": []}
    )

    result = scraper.fetch_by_url("https://example.com/wiki/Test")

    assert len(result) == 1
    assert result[0]["url"] == "https://example.com/wiki/Test"
    assert result[0]["infobox"]["name"] == "Test"


def test_single_scraper_returns_empty_list_when_not_circuit() -> None:
    scraper = DummySingleCircuitScraper(is_circuit=False, details=None)

    result = scraper.fetch_by_url("https://example.com/wiki/Test")

    assert result == []
