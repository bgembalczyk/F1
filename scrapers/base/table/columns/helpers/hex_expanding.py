from scrapers.base.table.columns.helpers.constants import CSS_3DIGIT_HEX_RE


def expand_hex_shorthand(color: str) -> str:
    """Expand a CSS 3-digit hex colour to its 6-digit equivalent.

    Examples::

        "#fcc" → "#ffcccc"
        "#abc" → "#aabbcc"
        "#ffcccc" → "#ffcccc"  (unchanged)

    Args:
        color: Lower-cased, space-stripped colour string.

    Returns:
        6-digit hex colour string, or the original string if it was not a
        3-digit shorthand.
    """
    if CSS_3DIGIT_HEX_RE.match(color):
        return "#" + "".join(c * 2 for c in color[1:])
    return color
