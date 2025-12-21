from __future__ import annotations

import pytest

from scrapers.constructors.privateer_teams_list import PrivateerTeamsListScraper


class StubFetcher:
    def __init__(self, html: str) -> None:
        self.html = html
        self.calls = 0

    def get_text(self, url: str, *, timeout: int | None = None) -> str:
        self.calls += 1
        return self.html


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
    scraper = PrivateerTeamsListScraper(fetcher=fetcher)

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

    scraper = PrivateerTeamsListScraper(fetcher=StubFetcher(html))

    with pytest.raises(RuntimeError, match="Nie znaleziono sekcji"):
        scraper.get_data()
