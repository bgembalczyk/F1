# ruff: noqa: E501, PLR2004
from bs4 import BeautifulSoup

from scrapers.drivers.infobox.parsers.active_years import ActiveYearsParser


class MockLinkExtractor:
    def __init__(self, links: list[dict]) -> None:
        self._links = links

    def extract_links(self, _cell):
        return self._links


def cell(html: str):
    return BeautifulSoup(f"<td>{html}</td>", "html.parser").find("td")


def test_parse_active_years_single_year_no_links() -> None:
    parser = ActiveYearsParser(MockLinkExtractor([]))
    result = parser.parse_active_years(cell("2002"))
    assert result == [{"year": 2002, "url": None}]


def test_parse_active_years_multiple_individual_years() -> None:
    parser = ActiveYearsParser(MockLinkExtractor([]))
    result = parser.parse_active_years(cell("2002, 2005, 2007"))
    years = [r["year"] for r in result]
    assert sorted(years) == [2002, 2005, 2007]


def test_parse_active_years_range_expands() -> None:
    parser = ActiveYearsParser(MockLinkExtractor([]))
    result = parser.parse_active_years(cell("2007-2009"))
    years = [r["year"] for r in result]
    assert years == [2007, 2008, 2009]


def test_parse_active_years_attaches_url_from_link() -> None:
    links = [{"text": "2005", "url": "https://en.wikipedia.org/wiki/2005_F1_season"}]
    parser = ActiveYearsParser(MockLinkExtractor(links))
    result = parser.parse_active_years(cell("2005"))
    assert result[0]["url"] == "https://en.wikipedia.org/wiki/2005_F1_season"


def test_parse_active_years_interpolates_missing_url_in_range() -> None:
    links = [
        {
            "text": "2007",
            "url": "https://en.wikipedia.org/wiki/2007_Formula_One_season",
        },
    ]
    parser = ActiveYearsParser(MockLinkExtractor(links))
    result = parser.parse_active_years(cell("2007-2008"))
    result_by_year = {r["year"]: r["url"] for r in result}
    assert 2007 in result_by_year
    assert 2008 in result_by_year
    assert result_by_year[2007] is not None


def test_parse_active_years_empty_cell_returns_empty_list() -> None:
    parser = ActiveYearsParser(MockLinkExtractor([]))
    result = parser.parse_active_years(cell(""))
    assert result == []
