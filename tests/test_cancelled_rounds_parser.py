"""Tests for CancelledRoundsParser logic."""

import pytest
from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.seasons.parsers.cancelled_rounds import CancelledRoundsParser
from scrapers.seasons.parsers.table import SeasonTableParser


@pytest.fixture()
def parser():
    """Create a CancelledRoundsParser instance for testing."""
    options = ScraperOptions()
    table_parser = SeasonTableParser(
        options=options,
        include_urls=True,
        url="https://example.com/test",
    )
    return CancelledRoundsParser(table_parser)


def test_cancelled_rounds_returns_second_table_when_two_tables_in_section(
    parser,
) -> None:
    """When section has two tables, cancelled_rounds should be second."""
    html = """
    <html>
      <body>
        <h2><span id="Calendar">Calendar</span></h2>
        <table class="wikitable">
          <tr>
            <th>Round</th>
            <th>Grand Prix</th>
            <th>Circuit</th>
            <th>Date</th>
          </tr>
          <tr>
            <td>1</td>
            <td><a href="/wiki/Monaco_Grand_Prix">Monaco Grand Prix</a></td>
            <td>Monte Carlo</td>
            <td>May 1</td>
          </tr>
        </table>
        <table class="wikitable">
          <tr>
            <th>Grand Prix</th>
            <th>Circuit</th>
            <th>Date</th>
          </tr>
          <tr>
            <td><a href="/wiki/Belgian_Grand_Prix">Belgian Grand Prix</a></td>
            <td>Spa-Francorchamps</td>
            <td>June 1</td>
          </tr>
        </table>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    # Parse without calendar data (should return second table)
    result = parser.parse(soup, season_year=2020, calendar_data=None)

    assert len(result) == 1
    assert result[0]["grand_prix"]["text"] == "Belgian Grand Prix"
    # Circuit has nested structure: {'circuit': {'text': '...', 'url': ...}}
    assert result[0]["circuit"]["circuit"]["text"] == "Spa-Francorchamps"


def test_cancelled_rounds_returns_empty_when_one_table_matches_calendar(parser) -> None:
    """When there's 1 table and it matches calendar, return empty list."""
    html = """
    <html>
      <body>
        <h2><span id="Calendar">Calendar</span></h2>
        <table class="wikitable">
          <tr>
            <th>Grand Prix</th>
            <th>Circuit</th>
            <th>Date</th>
          </tr>
          <tr>
            <td><a href="/wiki/Monaco_Grand_Prix">Monaco Grand Prix</a></td>
            <td>Monte Carlo</td>
            <td>May 1</td>
          </tr>
        </table>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    # Create calendar data that matches the table
    # Note: The circuit structure is nested as {'circuit': {'text': '...', 'url': ...}}
    calendar_data = [
        {
            "round": 1,
            "grand_prix": {
                "text": "Monaco Grand Prix",
                "url": "/wiki/Monaco_Grand_Prix",
            },
            "circuit": {"circuit": {"text": "Monte Carlo", "url": None}},
            "race_date": "May 1",
        },
    ]

    # Parse with matching calendar data (should return empty)
    result = parser.parse(soup, season_year=2020, calendar_data=calendar_data)

    assert result == []


def test_cancelled_rounds_returns_table_when_one_table_differs_from_calendar(
    parser,
) -> None:
    """When there's 1 table and it differs from calendar, return it."""
    html = """
    <html>
      <body>
        <h2><span id="Cancelled_Grands_Prix">Cancelled Grands Prix</span></h2>
        <table class="wikitable">
          <tr>
            <th>Grand Prix</th>
            <th>Circuit</th>
            <th>Date</th>
          </tr>
          <tr>
            <td><a href="/wiki/Belgian_Grand_Prix">Belgian Grand Prix</a></td>
            <td>Spa-Francorchamps</td>
            <td>June 1</td>
          </tr>
        </table>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    # Create calendar data that differs from the table
    calendar_data = [
        {
            "round": 1,
            "grand_prix": {
                "text": "Monaco Grand Prix",
                "url": "/wiki/Monaco_Grand_Prix",
            },
            "circuit": {"circuit": {"text": "Monte Carlo", "url": None}},
            "race_date": "May 1",
        },
    ]

    # Parse with different calendar data (should return the table)
    result = parser.parse(soup, season_year=2020, calendar_data=calendar_data)

    assert len(result) == 1
    assert result[0]["grand_prix"]["text"] == "Belgian Grand Prix"


def test_cancelled_rounds_returns_empty_when_two_tables_and_second_matches_calendar(
    parser,
) -> None:
    """When section has two matching tables and the second matches calendar, return empty.

    Regression test: for seasons without cancelled rounds (e.g. 1950), the Calendar
    section may be followed by a results table that also has Grand Prix + Circuit columns.
    The second table used to be returned as cancelled rounds without checking the calendar.
    """
    html = """
    <html>
      <body>
        <h2><span id="Calendar">Calendar</span></h2>
        <table class="wikitable">
          <tr>
            <th>Round</th>
            <th>Grand Prix</th>
            <th>Circuit</th>
            <th>Date</th>
          </tr>
          <tr>
            <td>1</td>
            <td><a href="/wiki/Monaco_Grand_Prix">Monaco Grand Prix</a></td>
            <td>Monte Carlo</td>
            <td>May 1</td>
          </tr>
        </table>
        <table class="wikitable">
          <tr>
            <th>Round</th>
            <th>Grand Prix</th>
            <th>Circuit</th>
            <th>Pole position</th>
            <th>Fastest lap</th>
            <th>Winning driver</th>
          </tr>
          <tr>
            <td>1</td>
            <td><a href="/wiki/Monaco_Grand_Prix">Monaco Grand Prix</a></td>
            <td>Monte Carlo</td>
            <td><a href="/wiki/Fangio">Fangio</a></td>
            <td><a href="/wiki/Fangio">Fangio</a></td>
            <td><a href="/wiki/Fangio">Fangio</a></td>
          </tr>
        </table>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    calendar_data = [
        {
            "round": 1,
            "grand_prix": {
                "text": "Monaco Grand Prix",
                "url": "/wiki/Monaco_Grand_Prix",
            },
            "circuit": {"circuit": {"text": "Monte Carlo", "url": None}},
            "race_date": "May 1",
        },
    ]

    result = parser.parse(soup, season_year=1950, calendar_data=calendar_data)

    assert result == []


def test_cancelled_rounds_returns_empty_when_no_table_found(parser) -> None:
    """When no table is found in any section, return empty list."""
    html = """
    <html>
      <body>
        <h2><span id="Results">Results</span></h2>
        <p>No cancelled rounds this year.</p>
      </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    result = parser.parse(soup, season_year=2020, calendar_data=None)

    assert result == []
