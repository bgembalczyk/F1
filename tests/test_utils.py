import pytest

bs4 = pytest.importorskip("bs4")
try:
    from bs4 import BeautifulSoup
except ImportError:
    pytest.skip("bs4 lacks BeautifulSoup", allow_module_level=True)

from scrapers.base.helpers.utils import (
    extract_links_from_cell,
    is_reference_link,
    is_wikipedia_redlink,
)

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

if "bs4" not in sys.modules:
    bs4_module = types.ModuleType("bs4")

    class Tag:  # type: ignore
        pass

    bs4_module.Tag = Tag
    sys.modules["bs4"] = bs4_module

from scrapers.base.helpers.utils import parse_float_from_text, parse_int_from_text


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


def test_regular_link_is_not_reference():
    tag = _tag('<a href="/wiki/Example">Example</a>')

    assert not is_reference_link(tag)


def test_is_wikipedia_redlink():
    assert is_wikipedia_redlink(
        "https://en.wikipedia.org/w/index.php?title=Test&action=edit&redlink=1"
    )
    assert not is_wikipedia_redlink("https://en.wikipedia.org/wiki/Test")


def test_extract_links_handles_local_anchors_and_redlinks():
    soup = BeautifulSoup(
        """
        <td>
            <a href="#cite_note-1">[1]</a>
            <a href="#section">Section</a>
            <a href="/w/index.php?title=Missing&action=edit&redlink=1">Missing page</a>
            <a href="/wiki/Example">Example</a>
        </td>
        """,
        "html.parser",
    )

    links = extract_links_from_cell(
        soup.td, full_url=lambda href: f"https://en.wikipedia.org{href}"
    )

    assert links == [
        {"text": "Section", "url": "https://en.wikipedia.org#section"},
        {"text": "Missing page", "url": None},
        {"text": "Example", "url": "https://en.wikipedia.org/wiki/Example"},
    ]


@pytest.mark.parametrize(
    "text, expected",
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
    "text, expected",
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
