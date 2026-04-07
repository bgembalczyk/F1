# ruff: noqa: E501, PLR2004

from layers.zero.record_merge_ops import merge_driver_dict_values
from layers.zero.record_merge_ops import merge_driver_values
from layers.zero.record_merge_ops import merge_list_values
from layers.zero.record_merge_ops import merge_values


# merge_list_values - lines 9-20
def test_merge_list_values_deduplicates_identical_items() -> None:
    existing = [{"a": 1}, {"b": 2}]
    incoming = [{"a": 1}, {"c": 3}]
    result = merge_list_values(existing, incoming)
    assert result == [{"a": 1}, {"b": 2}, {"c": 3}]


def test_merge_list_values_preserves_order() -> None:
    existing = [1, 2, 3]
    incoming = [3, 4, 5]
    result = merge_list_values(existing, incoming)
    assert result == [1, 2, 3, 4, 5]


def test_merge_list_values_handles_empty_existing() -> None:
    assert merge_list_values([], [1, 2]) == [1, 2]


def test_merge_list_values_handles_empty_incoming() -> None:
    assert merge_list_values([1, 2], []) == [1, 2]


# merge_values - lines 34, 37
def test_merge_values_merges_dicts_recursively() -> None:
    existing = {"a": 1, "b": {"x": 10}}
    incoming = {"b": {"y": 20}, "c": 3}
    result = merge_values(existing, incoming)
    assert result == {"a": 1, "b": {"x": 10, "y": 20}, "c": 3}


def test_merge_values_merges_lists() -> None:
    result = merge_values([1, 2], [2, 3])
    assert result == [1, 2, 3]


def test_merge_values_returns_incoming_when_existing_is_none() -> None:
    assert merge_values(None, "hello") == "hello"


def test_merge_values_returns_incoming_when_existing_is_empty_string() -> None:
    assert merge_values("", "value") == "value"


def test_merge_values_returns_incoming_when_existing_is_empty_list() -> None:
    assert merge_values([], [1, 2]) == [1, 2]


def test_merge_values_keeps_existing_when_both_are_scalars() -> None:
    assert merge_values("original", "new") == "original"


# merge_driver_dict_values - lines 46-55
def test_merge_driver_dict_values_skips_entries_and_starts_keys() -> None:
    existing = {"wins": 5, "entries": 100, "starts": 90}
    incoming = {"wins": 3, "entries": 50, "starts": 40, "poles": 2}
    result = merge_driver_dict_values(existing, incoming)
    # entries and starts from incoming should NOT be merged
    assert result["entries"] == 100
    assert result["starts"] == 90
    assert result["poles"] == 2


def test_merge_driver_dict_values_merges_non_skip_keys() -> None:
    existing = {"wins": 5}
    incoming = {"wins": 3, "poles": 2}
    result = merge_driver_dict_values(existing, incoming)
    # existing wins kept (scalar), poles added
    assert result["wins"] == 5
    assert result["poles"] == 2


def test_merge_driver_dict_values_adds_new_keys_from_incoming() -> None:
    existing: dict = {}
    incoming = {"wins": 7}
    result = merge_driver_dict_values(existing, incoming)
    assert result["wins"] == 7


# merge_driver_values - lines 59-65
def test_merge_driver_values_merges_dicts() -> None:
    existing = {"wins": 5}
    incoming = {"poles": 3}
    result = merge_driver_values(existing, incoming)
    assert result == {"wins": 5, "poles": 3}


def test_merge_driver_values_merges_lists() -> None:
    result = merge_driver_values([1, 2], [2, 3])
    assert result == [1, 2, 3]


def test_merge_driver_values_returns_incoming_when_existing_falsy() -> None:
    assert merge_driver_values(None, "value") == "value"
    assert merge_driver_values("", "value") == "value"
    assert merge_driver_values([], [1]) == [1]


def test_merge_driver_values_keeps_existing_scalar() -> None:
    assert merge_driver_values("kept", "ignored") == "kept"
