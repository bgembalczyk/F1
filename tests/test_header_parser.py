"""Tests for wiki header parser and base parser contracts."""

import pytest

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.header import HeaderParser
from tests.fixtures.wiki_parser_utils import make_soup


def test_wiki_parser_is_abstract() -> None:
    with pytest.raises(TypeError):
        WikiParser()  # type: ignore[abstract]


def test_header_parser_extracts_title() -> None:
    html = """
    <header class="mw-body-header vector-page-titlebar no-font-mode-scale">
      <h1 class="mw-page-title-main">Lewis Hamilton</h1>
    </header>
    """
    parser = HeaderParser()

    result = parser.parse(make_soup(html).find("header"))

    assert result["title"] == "Lewis Hamilton"


def test_header_parser_find_header() -> None:
    html = """
    <html><body>
      <header class="mw-body-header vector-page-titlebar">
        <h1>Title</h1>
      </header>
    </body></html>
    """

    header_el = HeaderParser.find_header(make_soup(html))

    assert header_el is not None
    assert header_el.name == "header"


def test_header_parser_find_header_returns_none_when_absent() -> None:
    soup = make_soup("<html><body><div>No header here</div></body></html>")

    assert HeaderParser.find_header(soup) is None
