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
            # No special HTML structure - fall back to plain comma-split.
            return split_delimited_text(ctx.clean_text or "")

        raw_segments = self._extract_segments(cell)
        result: list[str] = []
        for seg in raw_segments:
            result.extend(split_delimited_text(seg))
        return result

    @staticmethod
    def _extract_segments(cell: Tag) -> list[str]:
        """Return text segments from *cell*.

        Treat ``<br>`` and ``<p>`` as separators.

        Rules
        -----
        * ``<br>`` - flushes the current accumulated text as a new segment.
        * ``<p>`` child - flushes any pre-paragraph text as a segment, then
          processes the ``<p>`` contents as a separate segment.  A ``<p>``
          whose entire (cleaned) text is wrapped in a single pair of
          parentheses (e.g. ``(Image of a woman ...)``) is skipped entirely.
        * All other inline elements contribute their plain text to the current
          accumulator.
        """
        segments: list[str] = []
        current_parts: list[str] = []

        for child in cell.children:
            if isinstance(child, Tag):
                ColourListColumn._handle_tag_child(child, segments, current_parts)
            elif isinstance(child, NavigableString):
                ColourListColumn._append_text_part(str(child), current_parts)

        ColourListColumn._flush_current_parts(segments, current_parts)
        return segments

    @staticmethod
    def _handle_tag_child(
        child: Tag,
        segments: list[str],
        current_parts: list[str],
    ) -> None:
        if child.name == "br":
            ColourListColumn._flush_current_parts(segments, current_parts)
            return
        if child.name == "p":
            ColourListColumn._flush_current_parts(segments, current_parts)
            ColourListColumn._append_paragraph_segment(child, segments)
            return
        ColourListColumn._append_text_part(
            child.get_text(" ", strip=True),
            current_parts,
        )

    @staticmethod
    def _append_paragraph_segment(child: Tag, segments: list[str]) -> None:
        p_text = child.get_text(" ", strip=True)
        p_cleaned = clean_wiki_text(p_text)
        if p_cleaned and not re.fullmatch(r"\(.*\)", p_cleaned.strip()):
            segments.append(p_cleaned)

    @staticmethod
    def _append_text_part(text: str, current_parts: list[str]) -> None:
        stripped = text.strip()
        if stripped:
            current_parts.append(stripped)

    @staticmethod
    def _flush_current_parts(segments: list[str], current_parts: list[str]) -> None:
        text = " ".join(current_parts).strip()
        current_parts.clear()
        if not text:
            return
        cleaned = clean_wiki_text(text)
        if cleaned:
            segments.append(cleaned)
