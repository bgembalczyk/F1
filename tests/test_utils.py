import pytest

try:
    from bs4 import BeautifulSoup
except Exception:
    pytest.skip("beautifulsoup4 is required for these tests", allow_module_level=True)

from scrapers.base.helpers.utils import is_reference_link

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
