import sys
import types

import pytest

from scrapers.base.helpers.text import split_delimited_text
from scrapers.base.helpers.text_normalization import (
    clean_text,
    is_language_link,
    normalize_dashes,
    strip_lang_suffix,
)
from scrapers.base.helpers.time import parse_time_seconds_from_text, parse_time_text
from scrapers.base.helpers.html_utils import clean_wiki_text, extract_links_from_cell
from scrapers.base.helpers.value_objects import NormalizedTime

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


def test_clean_text_normalizes_refs_dashes_and_lang_suffix():
    text = "  Foo\xa0bar [1] A - B (es)  "

    assert clean_text(text) == "Foo bar A-B"


def test_strip_refs_removes_bracketed_references():
    assert strip_refs("Foo [1] bar [note 2]") == "Foo  bar "


def test_normalize_dashes_compacts_spaces():
    assert normalize_dashes("A – B") == "A-B"
    assert normalize_dashes("A -B") == "A-B"
    assert normalize_dashes("A- B") == "A-B"


def test_strip_lang_suffix_ignores_word_endings():
    assert strip_lang_suffix("David Salvador (es)") == "David Salvador"
    assert strip_lang_suffix("Yamaha YZF-R9 ( de )") == "Yamaha YZF-R9"
    assert strip_lang_suffix("Silverstone circuit") == "Silverstone circuit"


def test_is_language_link_matches_language_wikipedia_urls():
    assert is_language_link("fr", "https://fr.wikipedia.org/wiki/Test") is True
    assert is_language_link("fr", "https://en.wikipedia.org/wiki/fr") is False


def test_split_delimited_text_respects_min_parts():
    assert split_delimited_text("a", min_parts=2) == []
    assert split_delimited_text("a, b; c / d") == ["a", "b", "c", "d"]


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

    def full_url(href: str) -> str:
        if href.startswith("http"):
            return href
        return f"https://en.wikipedia.org{href}"

    links = extract_links_from_cell(cell, full_url=full_url)

    assert links == [
        {"text": "Good", "url": "https://en.wikipedia.org/wiki/Good"},
        {"text": "Red", "url": None},
    ]


def test_extract_links_from_cell_handles_default_full_url():
    if not _HAS_BS4:
        pytest.skip("beautifulsoup4 is required for link extraction test")
    html = """
    <td>
        <a href="https://en.wikipedia.org/wiki/Good">Good</a>
        <a href="https://en.wikipedia.org/w/index.php?title=Red&action=edit&redlink=1">Red</a>
        <a href="https://fr.wikipedia.org/wiki/Test">fr</a>
        <a href="#cite_note-1">[1]</a>
    </td>
    """
    soup = BeautifulSoup(html, "html.parser")
    cell = soup.find("td")

    links = extract_links_from_cell(cell)

    assert links == [
        {"text": "Good", "url": "https://en.wikipedia.org/wiki/Good"},
        {"text": "Red", "url": None},
    ]


def test_parse_time_seconds_from_text_handles_various_inputs():
    assert parse_time_seconds_from_text(12.5) == 12.5
    assert parse_time_seconds_from_text("1:16.0357") == pytest.approx(76.0357)
    assert (
        parse_time_seconds_from_text({"text": "1:02.500"}) == pytest.approx(62.5)
    )
    assert (
        parse_time_seconds_from_text(NormalizedTime(text="0:59.9", seconds=None))
        == pytest.approx(59.9)
    )
    assert parse_time_seconds_from_text("no time") is None


def test_parse_time_text_prefers_text_fields():
    assert (
        parse_time_text(NormalizedTime(text="1:20.000", seconds=80.0)) == "1:20.000"
    )
    assert parse_time_text({"text": "  2:05.9 "}) == "2:05.9"
    assert parse_time_text(123.0) is None
