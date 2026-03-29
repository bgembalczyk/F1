"""Utilities shared by refactored base class architecture tests."""

from __future__ import annotations

from collections.abc import Iterable

WIKI_BASE_URL = "https://en.wikipedia.org/wiki"
INDIANAPOLIS_CONSTRUCTORS_URL = (
    f"{WIKI_BASE_URL}/List_of_Formula_One_constructors"
)
INDIANAPOLIS_ENGINE_MANUFACTURERS_URL = (
    f"{WIKI_BASE_URL}/List_of_Formula_One_engine_manufacturers"
)
POINTS_SYSTEMS_URL = (
    f"{WIKI_BASE_URL}/"
    "List_of_Formula_One_World_Championship_points_scoring_systems"
)


def assert_issubclass_cases(cases: Iterable[tuple[type, type]]) -> None:
    """Assert every (child, parent) pair follows Python class hierarchy."""
    for child, parent in cases:
        assert issubclass(child, parent), (
            f"{child.__name__} should inherit from {parent.__name__}"
        )


def assert_not_issubclass_cases(cases: Iterable[tuple[type, type]]) -> None:
    """Assert every (child, parent) pair is *not* in class hierarchy."""
    for child, parent in cases:
        assert not issubclass(child, parent), (
            f"{child.__name__} should not inherit from {parent.__name__}"
        )
