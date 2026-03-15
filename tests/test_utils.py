import pytest
from bs4 import BeautifulSoup

from scrapers.base.helpers.html_utils import find_section_elements
from scrapers.base.helpers.parsing import parse_float_from_text
from scrapers.base.helpers.parsing import parse_int_from_text
from scrapers.base.helpers.wiki import is_reference_link
from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin


def _tag(html: str):
    soup = BeautifulSoup(html, "html.parser")
    return soup.find("a")


def test_reference_link_via_cite_note():
    tag = _tag('<a href="#cite_note-1">[1]</a>')

    assert is_reference_link(tag)


def test_reference_link_via_class():
    tag = _tag('<a href="/wiki/Test" class="reference">[ref]</a>')

    assert is_reference_link(tag)


def test_local_anchor_without_text_is_reference_even_when_allowed():
    tag = _tag('<a href="#section"></a>')

    assert is_reference_link(tag, allow_local_anchors=True)


def test_local_anchor_with_text_respects_allow_local_anchors():
    tag = _tag('<a href="#section">Section</a>')

    assert not is_reference_link(tag, allow_local_anchors=True)
    assert is_reference_link(tag, allow_local_anchors=False)


@pytest.mark.parametrize(
    ("allow_local_anchors", "expected"),
    [
        (True, False),
        (False, True),
    ],
)
def test_local_anchor_with_text_allows_toggle(allow_local_anchors, expected):
    tag = _tag('<a href="#section">Section</a>')

    assert is_reference_link(tag, allow_local_anchors=allow_local_anchors) is expected


def test_regular_link_is_not_reference():
    tag = _tag('<a href="/wiki/Example">Example</a>')

    assert not is_reference_link(tag)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Population 1,234 people", 1234),
        ("+42 points", 42),
        ("", None),
        ("no digits here", None),
    ],
)
def test_parse_int_from_text(text, expected):
    assert parse_int_from_text(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Lap time +3.5s", 3.5),
        ("1,234.5 meters", 1234.5),
        ("1,234", 1234.0),
        ("", None),
        ("no number", None),
    ],
)
def test_parse_float_from_text(text, expected):
    assert parse_float_from_text(text) == expected


def test_find_section_elements_missing_heading():
    soup = BeautifulSoup("<div></div>", "html.parser")

    with pytest.raises(RuntimeError):
        find_section_elements(soup, "missing", ["table"])


def test_find_section_elements_returns_first_after_heading():
    html = """
    <h2><span id="intro">Intro</span></h2>
    <table id="before"></table>
    <h2><span id="target">Target</span></h2>
    <table class="wikitable" id="match-1"></table>
    <table class="wikitable" id="match-2"></table>
    """
    soup = BeautifulSoup(html, "html.parser")

    matches = find_section_elements(soup, "target", ["table"], class_="wikitable")

    assert matches[0]["id"] == "match-1"


def test_find_section_elements_without_section_id_returns_all_matches():
    html = """
    <h2><span id="intro">Intro</span></h2>
    <table class="wikitable" id="match-1"></table>
    <table class="wikitable" id="match-2"></table>
    """
    soup = BeautifulSoup(html, "html.parser")

    matches = find_section_elements(soup, None, ["table"], class_="wikitable")

    assert [match["id"] for match in matches] == ["match-1", "match-2"]


def test_split_url_fragment_returns_base_and_fragment():
    mixin = WikipediaSectionByIdMixin()

    base_url, fragment = mixin.split_url_fragment(
        "https://en.wikipedia.org/wiki/Foo#Bar_Baz",
    )

    assert base_url == "https://en.wikipedia.org/wiki/Foo"
    assert fragment == "Bar_Baz"


def test_split_url_fragment_handles_missing_fragment():
    mixin = WikipediaSectionByIdMixin()

    base_url, fragment = mixin.split_url_fragment("https://en.wikipedia.org/wiki/Foo")

    assert base_url == "https://en.wikipedia.org/wiki/Foo"
    assert fragment is None


def test_extract_section_by_id_with_text_alias_and_modern_heading_wrapper():
    html = """
    <div class="mw-heading mw-heading2"><h2 id="Career_results">Career result</h2></div>
    <table class="wikitable" id="t1"></table>
    <div class="mw-heading mw-heading2"><h2 id="Other">Other</h2></div>
    <table class="wikitable" id="t2"></table>
    """
    soup = BeautifulSoup(html, "html.parser")

    section = WikipediaSectionByIdMixin.extract_section_by_id(
        soup,
        "Career_results",
        domain="drivers",
    )

    assert section is not None
    assert section.find(id="t1") is not None
    assert section.find(id="t2") is None
