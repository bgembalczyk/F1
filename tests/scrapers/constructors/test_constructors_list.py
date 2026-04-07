# ruff: noqa: E501, PLR2004, SLF001
from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.constructors.constructors_list import ConstructorsListScraper
from scrapers.constructors.constructors_list import _PrivateerTeamsListParser
from scrapers.constructors.constructors_list import _PrivateerTeamsSectionParser


def _li(html: str) -> Tag:
    return BeautifulSoup(f"<ul>{html}</ul>", "html.parser").find("li")


def _ul(html: str) -> Tag:
    return BeautifulSoup(html, "html.parser").find("ul")


class TestPrivateerTeamsListParser:
    def test_parse_returns_items_from_li_elements(self) -> None:
        parser = _PrivateerTeamsListParser()
        ul = BeautifulSoup(
            '<ul><li><a href="/wiki/Williams">Williams</a> (1950-1960)</li></ul>',
            "html.parser",
        ).find("ul")
        result = parser.parse(ul)
        assert "items" in result
        assert len(result["items"]) == 1
        assert result["items"][0]["team"] == "Williams"

    def test_parse_item_returns_none_without_anchor(self) -> None:
        li = BeautifulSoup("<li>No link here</li>", "html.parser").find("li")
        result = _PrivateerTeamsListParser._parse_item(li)
        assert result is None

    def test_parse_item_returns_none_for_empty_team_name(self) -> None:
        li = BeautifulSoup('<li><a href="/wiki/Team"></a></li>', "html.parser").find(
            "li",
        )
        result = _PrivateerTeamsListParser._parse_item(li)
        assert result is None

    def test_parse_item_includes_href_as_team_url(self) -> None:
        li = BeautifulSoup(
            '<li><a href="/wiki/Ferrari">Ferrari</a></li>',
            "html.parser",
        ).find("li")
        result = _PrivateerTeamsListParser._parse_item(li)
        assert result is not None
        assert result["team_url"] == "/wiki/Ferrari"

    def test_parse_item_strips_flagicon_spans(self) -> None:
        li = BeautifulSoup(
            '<li><span class="flagicon">🇮🇹</span><a href="/wiki/Ferrari">Ferrari</a></li>',
            "html.parser",
        ).find("li")
        result = _PrivateerTeamsListParser._parse_item(li)
        assert result is not None
        assert result["team"] == "Ferrari"

    def test_parse_item_extracts_seasons_from_parentheses(self) -> None:
        li = BeautifulSoup(
            '<li><a href="/wiki/Williams">Williams</a> (1950-1960)</li>',
            "html.parser",
        ).find("li")
        result = _PrivateerTeamsListParser._parse_item(li)
        assert result is not None
        assert "seasons" in result

    def test_parse_item_no_seasons_without_parentheses(self) -> None:
        li = BeautifulSoup(
            '<li><a href="/wiki/Williams">Williams</a></li>',
            "html.parser",
        ).find("li")
        result = _PrivateerTeamsListParser._parse_item(li)
        assert result is not None
        assert "seasons" not in result


class TestPrivateerTeamsSectionParser:
    def test_parse_ul_element_directly(self) -> None:
        parser = _PrivateerTeamsSectionParser()
        ul = BeautifulSoup(
            '<ul><li><a href="/wiki/Williams">Williams</a></li></ul>',
            "html.parser",
        ).find("ul")
        result = parser.parse(ul)
        assert "items" in result

    def test_parse_div_with_nested_ul(self) -> None:
        parser = _PrivateerTeamsSectionParser()
        div = BeautifulSoup(
            '<div><ul><li><a href="/wiki/Ferrari">Ferrari</a></li></ul></div>',
            "html.parser",
        ).find("div")
        result = parser.parse(div)
        assert "items" in result
        assert len(result["items"]) == 1

    def test_parse_group_returns_empty_items_without_list(self) -> None:
        parser = _PrivateerTeamsSectionParser()
        result = parser.parse_group([])
        assert result == {"items": []}

    def test_parse_group_finds_ul_in_elements(self) -> None:
        parser = _PrivateerTeamsSectionParser()
        ul = BeautifulSoup(
            '<ul><li><a href="/wiki/McLaren">McLaren</a></li></ul>',
            "html.parser",
        ).find("ul")
        result = parser.parse_group([ul])
        assert "items" in result
        assert len(result["items"]) == 1


class TestConstructorsListScraperInit:
    def test_raises_for_unsupported_export_scope(self) -> None:
        import pytest

        with pytest.raises(ValueError, match="Unsupported export_scope"):
            ConstructorsListScraper(export_scope="invalid_scope")

    def test_initializes_with_valid_scopes(self) -> None:
        for scope in ("all", "current", "former", "indianapolis", "privateer"):
            scraper = ConstructorsListScraper(export_scope=scope)
            assert scraper._export_scope == scope

    def test_split_export_records_initialized_empty(self) -> None:
        scraper = ConstructorsListScraper(export_scope="all")
        for key, val in scraper._split_export_records.items():
            assert val == [], f"Expected empty list for key {key}"

    def test_split_export_path_generates_correct_stem(self) -> None:
        from pathlib import Path

        path = Path("/output/results.json")
        result = ConstructorsListScraper._split_export_path(
            path,
            "current_constructors",
        )
        assert result.name == "results_current_constructors.json"
        assert result.parent == path.parent
