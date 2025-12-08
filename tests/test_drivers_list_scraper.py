from pathlib import Path
import sys

import pytest

try:
    from bs4 import BeautifulSoup
except Exception:
    from tests.bs4_stub import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from scrapers.drivers.F1_drivers_list_scraper import F1DriversListScraper


def test_f1_drivers_list_scraper_smoke():
    html = """
    <html>
      <body>
        <h2 id="Drivers">Drivers</h2>
        <table class="wikitable">
          <tr>
            <th>Driver name</th>
            <th>Nationality</th>
            <th>Seasons competed</th>
            <th>Drivers' Championships</th>
          </tr>
          <tr>
            <td><a href="/wiki/Driver_A">Driver A*</a></td>
            <td>Country A</td>
            <td>2020–2021</td>
            <td>0</td>
          </tr>
          <tr>
            <td><a href="/wiki/Driver_B">Driver B^</a></td>
            <td>Country B</td>
            <td>2019, 2022</td>
            <td>2\n2019, 2022</td>
          </tr>
        </table>
      </body>
    </html>
    """

    scraper = F1DriversListScraper(include_urls=True)
    scraper._download = lambda: html  # type: ignore[attr-defined]

    rows = scraper.fetch()

    assert len(rows) == 2

    assert rows[0]["driver"]["text"] == "Driver A"
    assert rows[1]["driver"]["text"] == "Driver B"

    championships = rows[1]["drivers_championships"]
    assert championships["count"] == 2
    assert [s["year"] for s in championships["seasons"]] == [2019, 2022]

    seasons_competed = [season["year"] for season in rows[0]["seasons_competed"]]
    assert seasons_competed == [2020, 2021]
