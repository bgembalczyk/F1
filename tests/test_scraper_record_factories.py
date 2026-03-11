from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

from scrapers.base.options import ScraperOptions
from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.drivers.list_scraper import F1DriversListScraper

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
    pytest.skip("bs4 is required for scraper tests", allow_module_level=True)


class StubFetcher:
    def __init__(self, html: str) -> None:
        self.html = html

    def get_text(self, url: str, *, timeout: int | None = None) -> str:
        return self.html

    def get(self, url: str) -> str:
        return self.get_text(url)


def test_circuits_list_record_factory_defaults_lists() -> None:
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

    assert data == [
        {
            "circuit": {
                "text": "Test Circuit",
                "url": "https://en.wikipedia.org/wiki/Test_Circuit",
            },
            "circuit_status": "former",
            "type": "Street",
            "location": "Test City",
            "country": "Testland",
            "grands_prix": [],
            "seasons": [],
        }
    ]


def test_drivers_list_record_factory_populates_championships() -> None:
    html = """
    <html>
      <body>
        <h2><span id="Drivers">Drivers</span></h2>
        <table class="wikitable">
          <tr>
            <th>Driver name</th>
            <th>Nationality</th>
            <th>Seasons competed</th>
            <th>Drivers' Championships</th>
          </tr>
          <tr>
            <td><a href="/wiki/Test_Driver">Test Driver~</a></td>
            <td>Exampleland</td>
            <td>2005–2006</td>
            <td>2<br/>2005–2006</td>
          </tr>
        </table>
      </body>
    </html>
    """
    scraper = F1DriversListScraper(
        options=ScraperOptions(fetcher=StubFetcher(html), include_urls=True),
    )

    data = scraper.get_data()

    assert data == [
        {
            "driver": {
                "text": "Test Driver",
                "url": "https://en.wikipedia.org/wiki/Test_Driver",
            },
            "is_active": True,
            "is_world_champion": False,
            "nationality": "Exampleland",
            "seasons_competed": [
                {
                    "year": 2005,
                    "url": "https://en.wikipedia.org/wiki/2005_Formula_One_World_Championship",
                },
                {
                    "year": 2006,
                    "url": "https://en.wikipedia.org/wiki/2006_Formula_One_World_Championship",
                },
            ],
            "drivers_championships": {
                "count": 2,
                "seasons": [
                    {
                        "year": 2005,
                        "url": "https://en.wikipedia.org/wiki/2005_Formula_One_World_Championship",
                    },
                    {
                        "year": 2006,
                        "url": "https://en.wikipedia.org/wiki/2006_Formula_One_World_Championship",
                    },
                ],
            },
        }
    ]
