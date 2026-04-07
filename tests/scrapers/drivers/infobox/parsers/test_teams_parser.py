# ruff: noqa: E501, PLR2004
from bs4 import BeautifulSoup

from scrapers.drivers.infobox.parsers.teams import TeamsParser


class _MockLinkExtractor:
    def __init__(self, links: list[dict]) -> None:
        self._links = links

    def extract_links(self, _cell):
        return list(self._links)


def _cell(html: str):
    return BeautifulSoup(f"<td>{html}</td>", "html.parser").find("td")


def test_parse_teams_with_include_urls_returns_links() -> None:
    links = [
        {"text": "Ferrari", "url": "https://en.wikipedia.org/wiki/Ferrari"},
        {"text": "McLaren", "url": "https://en.wikipedia.org/wiki/McLaren"},
    ]
    parser = TeamsParser(_MockLinkExtractor(links), include_urls=True)
    result = parser.parse_teams(_cell("<a>Ferrari</a>, <a>McLaren</a>"))
    assert result == links


def test_parse_teams_without_include_urls_returns_text_list() -> None:
    parser = TeamsParser(_MockLinkExtractor([]), include_urls=False)
    result = parser.parse_teams(_cell("Ferrari, McLaren"))
    assert "Ferrari" in result
    assert "McLaren" in result


def test_parse_teams_without_include_urls_single_team() -> None:
    parser = TeamsParser(_MockLinkExtractor([]), include_urls=False)
    result = parser.parse_teams(_cell("Williams"))
    assert len(result) == 1


def test_parse_teams_without_include_urls_empty_cell_returns_empty() -> None:
    parser = TeamsParser(_MockLinkExtractor([]), include_urls=False)
    result = parser.parse_teams(_cell(""))
    assert result == []
