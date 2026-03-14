"""Utilities for parsing date fields with formula category markers."""

from scrapers.base.helpers.time import parse_date_text
from scrapers.base.table.columns.context import ColumnContext


def parse_date_with_category_marker(
    ctx: ColumnContext,
    category_marker: str,
) -> str | None:
    """
    Parse a date from ColumnContext, removing category markers (e.g., F2 marker).

    Args:
        ctx: The column context containing the date text.
        category_marker: The marker to remove (e.g., "#" for F2).

    Returns:
        The ISO format date string, or None if parsing fails.
    """
    text = (ctx.clean_text or "").replace(category_marker, "").strip()
    if not text:
        return None
    parsed = parse_date_text(text)
    iso = parsed.iso
    if isinstance(iso, list):
        return iso[0] if iso else None
    return iso


def parse_formula_category(ctx: ColumnContext, category_marker: str) -> str | None:
    """
    Parse the formula category from ColumnContext based on presence of category marker.

    Args:
        ctx: The column context containing the raw text.
        category_marker: The marker that indicates a different category
            (e.g., "#" for F2).

    Returns:
        "F2" if the marker is present in raw text, "F1" otherwise, or None if no text.
    """
    if not (ctx.raw_text or "").strip():
        return None
    return "F2" if category_marker in (ctx.raw_text or "") else "F1"
