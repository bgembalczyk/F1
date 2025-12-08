import sys
import types
from pathlib import Path

import pytest

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
