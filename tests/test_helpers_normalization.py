import sys
import types

import pytest

from scrapers.base.helpers.records import merge_two_records
from scrapers.base.helpers.text import split_delimited_text
from scrapers.base.helpers.wiki import clean_wiki_text, extract_links_from_cell

try:
    from bs4 import BeautifulSoup  # type: ignore
    _HAS_BS4 = True
except Exception:
    _HAS_BS4 = False
    bs4_module = types.ModuleType("bs4")

    class Tag:  # type: ignore
        pass

    class BeautifulSoup:  # type: ignore
        def __init__(self, *_args, **_kwargs):
            raise RuntimeError("BeautifulSoup not available in tests")

    bs4_module.Tag = Tag
    bs4_module.BeautifulSoup = BeautifulSoup
    sys.modules["bs4"] = bs4_module


def test_clean_wiki_text_removes_references_and_whitespace():
    text = "  Foo\xa0bar [1] [note 3]  "

    assert clean_wiki_text(text) == "Foo bar"


def test_split_delimited_text_respects_min_parts():
    assert split_delimited_text("a", min_parts=2) == []
    assert split_delimited_text("a, b; c / d") == ["a", "b", "c", "d"]


def test_merge_two_records_prefers_richer_data_and_normalizes_time():
    base = {"driver": {"text": "A"}, "time_seconds": 90.0, "year": "1999"}
    extra = {
        "driver": {"text": "A", "url": "https://example.com"},
        "time": "1:30.0",
        "series": {"text": "F1"},
    }

    merged = merge_two_records(base, extra)

    assert merged["driver"]["url"] == "https://example.com"
    assert merged["time"] == 90.0
    assert "time_seconds" not in merged


def test_extract_links_from_cell_filters_reference_and_language_links():
    if not _HAS_BS4:
        pytest.skip("beautifulsoup4 is required for link extraction test")
    html = """
    <td>
        <a href="/wiki/Good">Good</a>
        <a href="/w/index.php?title=Red&action=edit&redlink=1">Red</a>
        <a href="https://fr.wikipedia.org/wiki/Test">fr</a>
        <a href="#cite_note-1">[1]</a>
    </td>
    """
    soup = BeautifulSoup(html, "html.parser")
    cell = soup.find("td")

    def full_url(href):
        if not href:
            return None
        if href.startswith("http"):
            return href
        return f"https://en.wikipedia.org{href}"

    links = extract_links_from_cell(cell, full_url=full_url)

    assert links == [
        {"text": "Good", "url": "https://en.wikipedia.org/wiki/Good"},
        {"text": "Red", "url": None},
    ]
