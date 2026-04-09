from collections.abc import Callable

from scrapers.columns.context import ColumnContext


def create_suffix_checker(*markers: str) -> Callable[[ColumnContext], bool]:
    """
    Create a function that checks if raw text ends with any of the given markers.

    This is a factory function following the Factory pattern to create
    marker-checking predicates.

    Args:
        *markers: Suffix markers to check for

    Returns:
        Function that returns True if context raw_text ends with any marker
    """

    return lambda ctx: (ctx.raw_text or "").strip().endswith(markers)
