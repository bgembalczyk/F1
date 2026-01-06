import pytest
from bs4 import BeautifulSoup

from scrapers.base.helpers.text import (
    clean_wiki_text,
    extract_links_from_cell,
    strip_marks,
)
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.normalize import normalize_auto_value
from scrapers.base.helpers.text_normalization import (
    is_language_link,
    split_delimited_text,
)
from scrapers.base.helpers.time import parse_time_seconds_from_text, parse_time_text
from scrapers.base.helpers.url import normalize_url
from scrapers.base.helpers.value_objects import NormalizedTime


def test_clean_wiki_text_removes_references_and_whitespace():
    text = "  Foo\xa0bar [1] [note 3]  "

    assert clean_wiki_text(text) == "Foo bar"


def test_clean_wiki_text_normalizes_refs_dashes_and_lang_suffix():
    text = "  Foo\xa0bar [1] A - B (es)  "

    assert clean_wiki_text(text) == "Foo bar A-B"


def test_clean_wiki_text_can_preserve_refs():
    assert clean_wiki_text("Foo [1] bar [note 2]", strip_refs=False) == (
        "Foo [1] bar [note 2]"
    )


def test_clean_wiki_text_normalize_dashes_compacts_spaces():
    assert clean_wiki_text("A – B") == "A-B"
    assert clean_wiki_text("A -B") == "A-B"
    assert clean_wiki_text("A- B") == "A-B"


def test_clean_wiki_text_strip_lang_suffix_ignores_word_endings():
    assert (
        clean_wiki_text("David Salvador (es)", strip_lang_suffix=True)
        == "David Salvador"
    )
    assert (
        clean_wiki_text("Yamaha YZF-R9 ( de )", strip_lang_suffix=True)
        == "Yamaha YZF-R9"
    )
    assert (
        clean_wiki_text("Silverstone circuit", strip_lang_suffix=True)
        == "Silverstone circuit"
    )


def test_clean_wiki_text_accepts_html_tag_input():
    soup = BeautifulSoup("<span>Foo&nbsp;bar [1]</span>", "html.parser")

    assert clean_wiki_text(soup.span) == "Foo bar"


def test_is_language_link_matches_language_wikipedia_urls():
    assert is_language_link("fr", "https://fr.wikipedia.org/wiki/Test") is True
    assert is_language_link("fr", "https://en.wikipedia.org/wiki/fr") is False


def test_split_delimited_text_respects_min_parts():
    assert split_delimited_text("a", min_parts=2) == []
    assert split_delimited_text("a, b; c / d") == ["a", "b", "c", "d"]


def test_extract_links_from_cell_filters_reference_and_language_links():
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

    def full_url(href: str) -> str | None:
        return normalize_url("https://en.wikipedia.org", href)

    links = extract_links_from_cell(cell, full_url=full_url)

    assert links == [
        {"text": "Good", "url": "https://en.wikipedia.org/wiki/Good"},
        {"text": "Red", "url": None},
    ]


def test_extract_links_from_cell_handles_default_full_url():
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


def test_extract_links_from_cell_accepts_html_string():
    html = """
    <td>
        <a href="/wiki/Good">Good</a>
        <a href="#cite_note-1">[1]</a>
    </td>
    """
    links = extract_links_from_cell(html)

    assert links == [{"text": "Good", "url": "/wiki/Good"}]


def test_normalize_links_filters_empty_and_language_links_and_marks():
    links = [
        {"text": "", "url": "https://example.com/empty"},
        {"text": "Good*", "url": "https://example.com/good"},
        {"text": "Marked~", "url": "https://example.com/marked"},
        {"text": "Suffix (es)", "url": "https://example.com/suffix"},
        {"text": "fr", "url": "https://fr.wikipedia.org/wiki/Test"},
    ]

    assert normalize_links(links) == [
        {"text": "Good", "url": "https://example.com/good"},
        {"text": "Marked", "url": "https://example.com/marked"},
        {"text": "Suffix", "url": "https://example.com/suffix"},
    ]


def test_normalize_links_handles_none_and_single_link():
    assert normalize_links(None) == []
    assert normalize_links({"text": "Solo", "url": "https://example.com/solo"}) == [
        {"text": "Solo", "url": "https://example.com/solo"},
    ]


def test_normalize_links_keeps_missing_url():
    assert normalize_links({"text": "Plain", "url": None}) == [
        {"text": "Plain", "url": None},
    ]


def test_normalize_links_from_html_filters_references_and_multiple_links():
    html = """
    <td>
        <a href="/wiki/Good">Good</a>
        <a href="#cite_note-1">[1]</a>
        <a href="/wiki/Other">Other</a>
    </td>
    """
    soup = BeautifulSoup(html, "html.parser")
    cell = soup.find("td")

    def full_url(href: str) -> str | None:
        return normalize_url("https://en.wikipedia.org", href)

    assert normalize_links(cell, full_url=full_url) == [
        {"text": "Good", "url": "https://en.wikipedia.org/wiki/Good"},
        {"text": "Other", "url": "https://en.wikipedia.org/wiki/Other"},
    ]


def test_normalize_auto_value_handles_dict():
    value = {"text": "Marked†", "url": "https://example.com/marked"}

    assert normalize_auto_value(value, strip_marks=True) == {
        "text": "Marked",
        "url": "https://example.com/marked",
    }


def test_normalize_auto_value_handles_list():
    value = [{"text": "Marked*", "url": "https://example.com/marked"}]

    assert normalize_auto_value(value, strip_marks=True) == [
        {"text": "Marked", "url": "https://example.com/marked"},
    ]


def test_normalize_auto_value_handles_str():
    assert normalize_auto_value("Marked~", strip_marks=True) == "Marked"


def test_normalize_auto_value_handles_none():
    assert normalize_auto_value(None) is None


def test_strip_marks_handles_special_characters_and_tag():
    soup = BeautifulSoup("<span>Marked†*</span>", "html.parser")

    assert strip_marks(soup.span) == "Marked"


def test_normalize_auto_value_drops_empty_dict_text():
    value = {"text": "†", "url": "https://example.com/marked"}

    assert normalize_auto_value(value, strip_marks=True, drop_empty=True) is None


def test_normalize_auto_value_drops_empty_list():
    value = [{"text": "", "url": None}]

    assert normalize_auto_value(value, drop_empty=True) is None


def test_normalize_auto_value_drops_empty_str():
    assert normalize_auto_value("   ", drop_empty=True) is None


def test_parse_time_seconds_from_text_handles_various_inputs():
    assert parse_time_seconds_from_text(12.5) == 12.5
    assert parse_time_seconds_from_text("1:16.0357") == pytest.approx(76.0357)
    assert parse_time_seconds_from_text({"text": "1:02.500"}) == pytest.approx(62.5)
    assert parse_time_seconds_from_text(
        NormalizedTime(text="0:59.9", seconds=None)
    ) == pytest.approx(59.9)
    assert parse_time_seconds_from_text("no time") is None


def test_parse_time_text_prefers_text_fields():
    assert parse_time_text(NormalizedTime(text="1:20.000", seconds=80.0)) == "1:20.000"
    assert parse_time_text({"text": "  2:05.9 "}) == "2:05.9"
    assert parse_time_text(123.0) is None


def test_normalize_url_builds_and_validates() -> None:
    base = "https://en.wikipedia.org/wiki/Foo"

    assert normalize_url(base, "/wiki/Bar") == "https://en.wikipedia.org/wiki/Bar"
    assert (
        normalize_url(base, "//en.wikipedia.org/wiki/Baz")
        == "https://en.wikipedia.org/wiki/Baz"
    )
    assert normalize_url(base, "https://example.com/path") == "https://example.com/path"
    assert normalize_url(base, "mailto:test@example.com") is None
    assert normalize_url(base, "https://example.com//double") is None
