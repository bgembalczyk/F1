"""Constructor-specific parsing helpers.

This module contains helper functions for parsing constructor-related data
from Wikipedia tables.
Extracted from scrapers/base/table/columns/helpers.py to follow SRP.

Follows SOLID principles:
- Single Responsibility: Handles only constructor-related parsing
- High Cohesion: All functions work together for constructor parsing
- Information Expert: Constructor parsing logic grouped with constructor data
"""

from bs4 import NavigableString
from bs4 import Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.constants import ENGINE_CONSTRUCTOR_INDEX
from scrapers.base.table.columns.helpers.constants import HYPHEN_CHARS


class ConstructorParsingHelpers:
    """
    Helper class for parsing constructor information from table cells.

    Provides methods for:
    - Splitting constructor cells by line breaks
    - Extracting constructor parts from multi-line cells
    - Parsing constructor segments
    """

    @staticmethod
    def _split_cell_children(ctx: ColumnContext) -> list[list[object]]:
        lines: list[list[object]] = [[]]
        for child in ctx.cell.children:
            if isinstance(child, Tag) and child.name == "br":
                lines.append([])
                continue
            lines[-1].append(child)
        return lines

    @staticmethod
    def _count_line_links(line: list[object]) -> int:
        return sum(
            1 if node.name == "a" else len(node.find_all("a"))
            for node in line
            if isinstance(node, Tag)
        )

    @staticmethod
    def _extract_line_text(line: list[object]) -> str:
        text_parts = []
        for node in line:
            node_text = (
                node.get_text(" ", strip=True)
                if isinstance(node, Tag)
                else str(node).strip()
            )
            if node_text:
                text_parts.append(node_text)
        return clean_wiki_text(" ".join(text_parts))

    @staticmethod
    def _build_line_context(
        ctx: ColumnContext,
        clean_text: str,
        line_links: list[LinkRecord],
    ) -> ColumnContext:
        return ColumnContext(
            cell=None,
            raw_text=clean_text,
            clean_text=clean_text,
            links=line_links,
            header=getattr(ctx, "header", None),
            key=getattr(ctx, "key", None),
            base_url=ctx.base_url,
            skip_sentinel=getattr(ctx, "skip_sentinel", None),
            model_fields=getattr(ctx, "model_fields", None),
            header_link=getattr(ctx, "header_link", None),
        )

    @staticmethod
    def split_lines(ctx: ColumnContext) -> list[ColumnContext]:
        """
        Split constructor cell into multiple contexts, one per line.

        Handles cells with multiple constructors separated by <br> tags.
        Distributes links across the split contexts.

        Args:
            ctx: Column context with potentially multi-line cell

        Returns:
            List of contexts, one per constructor line
        """
        if not ctx.cell:
            return []

        lines = ConstructorParsingHelpers._split_cell_children(ctx)
        line_link_counts = [
            ConstructorParsingHelpers._count_line_links(line) for line in lines
        ]

        line_contexts: list[ColumnContext] = []
        link_index = 0
        for line, link_count in zip(lines, line_link_counts, strict=False):
            line_links = ctx.links[link_index : link_index + link_count]
            link_index += link_count
            clean_text = ConstructorParsingHelpers._extract_line_text(line)
            line_contexts.append(
                ConstructorParsingHelpers._build_line_context(
                    ctx,
                    clean_text,
                    line_links,
                ),
            )

        return line_contexts

    @staticmethod
    def extract_part(ctx: ColumnContext, index: int) -> LinkRecord | None:
        """
        Extract specific constructor part by index from context.

        For cells with multiple constructors, extracts the nth one.

        Args:
            ctx: Column context
            index: Zero-based index of constructor to extract

        Returns:
            LinkRecord for the constructor, or None if index out of range
        """
        if not ctx.links:
            hyphen_split = ConstructorParsingHelpers.split_on_external_hyphen(ctx)
            if hyphen_split is None:
                return None
            parts = [hyphen_split[0], hyphen_split[1]]
            if index >= len(parts):
                return None
            part = clean_wiki_text(parts[index])
            return {"text": part, "url": None} if part else None

        if index >= len(ctx.links):
            # When a single link is present, it can represent both
            # chassis and engine constructor.
            # Return index 0 (chassis) also as index 1 (engine)
            # so both fields are populated.
            if index == ENGINE_CONSTRUCTOR_INDEX and len(ctx.links) == 1:
                return ctx.links[0]
            return None

        return ctx.links[index]

    @staticmethod
    def split_on_external_hyphen(ctx: ColumnContext) -> tuple[str, str] | None:
        """
        Split text on external hyphen (not part of links).

        Used for entries like "Constructor - Details" where hyphen is outside links.

        Args:
            ctx: Column context with text to split

        Returns:
            Tuple of (before_hyphen, after_hyphen), or None if no external hyphen
        """
        text = ctx.clean_text or ctx.raw_text or ""

        if " - " in text:
            parts = text.split(" - ", 1)
            return parts[0].strip(), parts[1].strip()

        return None

    @staticmethod
    def find_hyphen_split_index(ctx: ColumnContext) -> int | None:
        """
        Detect if a hyphen separator between links divides a multi-link chassis
        from the engine constructor.

        Iterates over the direct children of the cell looking for a hyphen
        NavigableString that appears after two or more ``<a>`` elements.  When
        found, returns the number of direct ``<a>`` children with non-empty text
        that precede the hyphen (i.e. the index at which ``ctx.links`` should be
        split: pre-hyphen links are the chassis, post-hyphen links the engine).

        Returns ``None`` when:
        - there is no cell,
        - no hyphen is found between links, or
        - one or fewer ``<a>`` elements precede the hyphen (the standard
          two-link case, which the existing ``ConstructorPartColumn``
          already handles correctly).

        Args:
            ctx: Column context containing the cell to inspect.

        Returns:
            Number of chassis links (split index into ``ctx.links``), or None.
        """
        if not ctx.cell:
            return None

        non_empty_a_before = 0
        hyphen_found = False

        for child in ctx.cell.children:
            if isinstance(child, Tag):
                if child.name == "a":
                    if hyphen_found:
                        # At least one link exists after the hyphen; commit split.
                        return non_empty_a_before if non_empty_a_before > 1 else None
                    link_text = child.get_text(strip=True)
                    if link_text:
                        non_empty_a_before += 1
            elif isinstance(child, NavigableString):
                stripped = str(child).strip()
                if stripped in HYPHEN_CHARS and non_empty_a_before > 1:
                    hyphen_found = True

        return None

    @staticmethod
    def extract_layout_text(clean_text: str, link_text: str) -> str | None:
        """
        Extract layout/configuration text, excluding link text.

        Args:
            clean_text: Full cleaned text from cell
            link_text: Text that appears in a link (to be removed)

        Returns:
            Layout text with link text removed, or None if empty
        """
        if not clean_text:
            return None

        if link_text:
            lower_clean = clean_text.lower()
            lower_link = link_text.lower()
            idx = lower_clean.find(lower_link)
            if idx != -1:
                clean_text = (
                    clean_text[:idx] + clean_text[idx + len(link_text) :]
                ).strip()

        clean_text = clean_text.strip(" -()")
        if not clean_text:
            return None

        if link_text and clean_text.lower() == link_text.lower():
            return None

        return clean_text
