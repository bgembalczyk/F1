from __future__ import annotations

import sys
from pathlib import Path

from scrapers.base.options import ScraperOptions
from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.drivers.list_scraper import F1DriversListScraper
from tests.support.dependency_stubs import ensure_optional_deps

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

ensure_optional_deps(
    require_bs4=True,
    bs4_skip_reason="bs4 is required for scraper tests",
)


class StubFetcher:
    def __init__(self, html: str) -> None:
        self.html = html

    def get_text(self, _url: str, *, _timeout: int | None = None) -> str:
        return self.html

    def get(self, _url: str) -> str:
        return self.get_text(_url)


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
            "last_length_used_km": None,
            "last_length_used_mi": None,
            "turns": None,
            "grands_prix_held": None,
            "grands_prix": [],
            "seasons": [],
        },
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
            <td>2005-2006</td>
            <td>2<br/>2005-2006</td>
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
            "is_world_champion": True,
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
            "race_entries": None,
            "race_starts": None,
            "pole_positions": None,
            "race_wins": None,
            "podiums": None,
            "fastest_laps": None,
        },
    ]
