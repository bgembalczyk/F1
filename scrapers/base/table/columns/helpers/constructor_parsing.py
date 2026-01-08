"""Constructor-specific parsing helpers.

This module contains helper functions for parsing constructor-related data from Wikipedia tables.
Extracted from scrapers/base/table/columns/helpers.py to follow SRP.

Follows SOLID principles:
- Single Responsibility: Handles only constructor-related parsing
- High Cohesion: All functions work together for constructor parsing
- Information Expert: Constructor parsing logic grouped with constructor data
"""
from typing import Optional

from bs4 import Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.table.columns.context import ColumnContext


class ConstructorParsingHelpers:
    """
    Helper class for parsing constructor information from table cells.
    
    Provides methods for:
    - Splitting constructor cells by line breaks
    - Extracting constructor parts from multi-line cells
    - Parsing constructor segments
    """

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

        lines: list[list[object]] = [[]]
        for child in ctx.cell.children:
            if isinstance(child, Tag) and child.name == "br":
                lines.append([])
                continue
            lines[-1].append(child)

        if not lines:
            return []

        # Count links in each line
        line_link_counts = []
        for line in lines:
            link_count = 0
            for node in line:
                if isinstance(node, Tag):
                    if node.name == "a":
                        link_count += 1
                    else:
                        link_count += len(node.find_all("a"))
            line_link_counts.append(link_count)

        # Create contexts for each line with proper link distribution
        line_contexts: list[ColumnContext] = []
        link_index = 0
        for line, link_count in zip(lines, line_link_counts):
            line_links = ctx.links[link_index : link_index + link_count]
            link_index += link_count

            text_parts = []
            for node in line:
                if isinstance(node, Tag):
                    node_text = node.get_text(" ", strip=True)
                else:
                    node_text = str(node).strip()
                if node_text:
                    text_parts.append(node_text)

            clean_text = clean_wiki_text(" ".join(text_parts))
            
            line_contexts.append(
                ColumnContext(
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
            return None
        
        if index >= len(ctx.links):
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
        
        # Look for patterns like " - " or " – " (various dash types)
        for separator in [" - ", " – ", " — "]:
            if separator in text:
                parts = text.split(separator, 1)
                if len(parts) == 2:
                    return parts[0].strip(), parts[1].strip()
        
        return None

    @staticmethod
    def extract_layout_text(clean_text: str, link_text: str) -> Optional[str]:
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
                clean_text = (clean_text[:idx] + clean_text[idx + len(link_text) :]).strip()

        clean_text = clean_text.strip(" -–—()")
        if not clean_text:
            return None

        if link_text and clean_text.lower() == link_text.lower():
            return None

        return clean_text
