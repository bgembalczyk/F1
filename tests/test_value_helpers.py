import pytest

from models.value_objects.helpers import normalize_iso
from models.value_objects.helpers import normalize_text


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, None),
        ("  ", None),
        ("  Monaco  ", "Monaco"),
        (123, "123"),
    ],
)
def test_normalize_text(value, expected):
    assert normalize_text(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, None),
        ([], None),
        ([" 2024-03-01 "], "2024-03-01"),
        (["  "], None),
        (" 2024-03-02 ", "2024-03-02"),
    ],
)
def test_normalize_iso(value, expected):
    assert normalize_iso(value) == expected
