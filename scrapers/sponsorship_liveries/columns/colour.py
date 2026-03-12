import re
from typing import Any

from bs4 import NavigableString
from bs4 import Tag

from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.text_normalization import split_delimited_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class ColourListColumn(BaseColumn):
    """Column for colour-list cells.

    Extends the plain :class:`~scrapers.base.table.columns.types.list.ListColumn`
    behaviour by processing HTML structure directly so that ``<br>`` tags and
    ``<p>`` element boundaries act as value separators (in the same way a
    comma would).

    Additionally, ``<p>`` children that consist entirely of parenthetical text
    (e.g. image descriptions such as
    ``(Image of a woman holding a box of Rizla+. cigarette papers)``) are
    silently ignored and do not contribute any colours to the output.
    """

    def parse(self, ctx: ColumnContext) -> Any:
        cell = ctx.cell
        if cell is None or (not cell.find("br") and not cell.find("p")):
            # No special HTML structure – fall back to plain comma-split.
            return split_delimited_text(ctx.clean_text or "")

        raw_segments = self._extract_segments(cell)
        result: list[str] = []
        for seg in raw_segments:
            result.extend(split_delimited_text(seg))
        return result

    @staticmethod
    def _extract_segments(cell: Tag) -> list[str]:
        """Return text segments from *cell*, treating ``<br>`` and ``<p>`` as separators.

        Rules
        -----
        * ``<br>`` – flushes the current accumulated text as a new segment.
        * ``<p>`` child – flushes any pre-paragraph text as a segment, then
          processes the ``<p>`` contents as a separate segment.  A ``<p>``
          whose entire (cleaned) text is wrapped in a single pair of
          parentheses (e.g. ``(Image of a woman ...)``) is skipped entirely.
        * All other inline elements contribute their plain text to the current
          accumulator.
        """
        segments: list[str] = []
        current_parts: list[str] = []

        def _flush() -> None:
            text = " ".join(current_parts).strip()
            current_parts.clear()
            if text:
                cleaned = clean_wiki_text(text)
                if cleaned:
                    segments.append(cleaned)

        for child in cell.children:
            if isinstance(child, Tag):
                if child.name == "br":
                    _flush()
                elif child.name == "p":
                    _flush()
                    p_text = child.get_text(" ", strip=True)
                    p_cleaned = clean_wiki_text(p_text)
                    # Skip <p> that is purely a parenthetical annotation
                    # (e.g. an image description).
                    if p_cleaned and not re.fullmatch(r"\(.*\)", p_cleaned.strip()):
                        segments.append(p_cleaned)
                else:
                    t = child.get_text(" ", strip=True)
                    if t:
                        current_parts.append(t)
            elif isinstance(child, NavigableString):
                t = str(child).strip()
                if t:
                    current_parts.append(t)

        _flush()
        return segments
