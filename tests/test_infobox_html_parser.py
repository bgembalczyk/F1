import pytest
import sys
import types

try:
    from bs4 import BeautifulSoup
except Exception:
    pytest.skip("beautifulsoup4 is required for these tests", allow_module_level=True)

from scrapers.base.infobox.html_parser import InfoboxHtmlParser


if "bs4" not in sys.modules:
    bs4_module = types.ModuleType("bs4")

    class Tag:  # type: ignore
        pass

    bs4_module.Tag = Tag
    sys.modules["bs4"] = bs4_module


def test_parser_extracts_title_rows_and_links():
    html = """
    <table class="infobox vcard">
        <caption>Test Circuit</caption>
        <tr>
            <th>Location</th>
            <td>
                <a href="/wiki/Test">Test Link</a>
                <a href="#cite_note-1">[1]</a>
            </td>
        </tr>
        <tr>
            <th>Owner</th>
            <td>Example Owner</td>
        </tr>
        <tr>
            <td>
                <table>
                    <tr>
                        <th>Nested</th>
                        <td>Ignore</td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    parser = InfoboxHtmlParser()

    result = parser.parse(soup)

    assert result["title"] == "Test Circuit"
    assert result["rows"]["Location"]["text"] == "Test Link [1]"
    assert result["rows"]["Location"]["links"] == [
        {"text": "Test Link", "url": "https://en.wikipedia.org/wiki/Test"}
    ]
    assert result["rows"]["Owner"]["text"] == "Example Owner"
    assert "Nested" not in result["rows"]


def test_parser_returns_empty_payload_without_infobox():
    soup = BeautifulSoup("<div>No infobox here</div>", "html.parser")
    parser = InfoboxHtmlParser()

    assert parser.parse(soup) == {"title": None, "rows": {}}
