from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.table.parser import HtmlTableParser
from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.context import WikiParserContext
from scrapers.wiki.parsers.elements.table import TableParser


class ArticleTablesParser(WikiParser):
    """Wspólny parser tabel wikitable z artykułów Wikipedii."""

    def __init__(
        self,
        *,
        include_heading_path: bool = False,
        include_source_table: bool = False,
    ) -> None:
        self.include_heading_path = include_heading_path
        self.include_source_table = include_source_table
        self._table_parser = TableParser()
        self._html_table_parser = HtmlTableParser()

    def parse(self, element: Tag | BeautifulSoup, context: WikiParserContext | None = None) -> list[dict[str, Any]]:
        tables: list[dict[str, Any]] = []
        base_context = context or WikiParserContext.empty()
        for index, table in enumerate(element.find_all("table", class_="wikitable"), start=1):
            table_context = base_context.for_table(index)
            parsed = self.parse_table(table, context=table_context)
            if parsed is not None:
                tables.append(parsed)
        return tables

    def parse_table(
        self,
        table: Tag,
        context: WikiParserContext | None = None,
    ) -> dict[str, Any] | None:
        headers, rows = self._parse_with_html_table_parser(table)
        if not headers:
            headers, rows = self._parse_with_legacy_parser(table, context=context)

        if not headers:
            return None

        filtered_rows = [row for row in rows if any(value.strip() for value in row.values())]
        if not filtered_rows:
            return None

        ctx = context or WikiParserContext.empty()
        parsed: dict[str, Any] = {
            "headers": headers,
            "rows": filtered_rows,
            "context": {
                "source_url": ctx.source_url,
                "section_path": list(ctx.section_path),
                "heading_id": ctx.heading_id,
                "table_index": ctx.table_index,
                "language": ctx.language,
            },
        }

        caption = self._extract_caption(table)
        if caption:
            parsed["caption"] = caption

        if self.include_heading_path:
            heading_path = self._heading_context(table)
            if heading_path:
                parsed["heading_path"] = heading_path

        if self.include_source_table:
            parsed["_table"] = table

        return parsed

    def _parse_with_html_table_parser(self, table: Tag) -> tuple[list[str], list[dict[str, str]]]:
        try:
            rows = self._html_table_parser.parse_table(table)
        except RuntimeError:
            return [], []

        if not rows:
            return [], []

        normalized_headers = self._normalize_headers(rows[0].headers)
        parsed_rows: list[dict[str, str]] = []
        for row in rows:
            values = [self._clean_text(cell.get_text(" ", strip=True)) for cell in row.cells]
            parsed_rows.append(dict(zip(normalized_headers, values, strict=False)))

        return normalized_headers, parsed_rows

    def _parse_with_legacy_parser(
        self,
        table: Tag,
        context: WikiParserContext | None = None,
    ) -> tuple[list[str], list[dict[str, str]]]:
        raw = self._table_parser.parse(table, context=context)
        headers = self._normalize_headers(raw.get("headers", []))
        rows: list[dict[str, str]] = []
        for row_cells in raw.get("rows", []):
            cells = [self._clean_text(cell) for cell in row_cells]
            rows.append(dict(zip(headers, cells, strict=False)))
        return headers, rows

    def _normalize_headers(self, headers: list[str]) -> list[str]:
        return [self._clean_text(header) for header in headers if self._clean_text(header)]

    def _extract_caption(self, table: Tag) -> str | None:
        caption_tag = table.find("caption")
        if caption_tag is None:
            return None
        caption = self._clean_text(caption_tag.get_text(" ", strip=True))
        return caption or None

    @staticmethod
    def _clean_text(value: str) -> str:
        return clean_wiki_text(value)

    def _heading_context(self, table: Tag) -> list[str]:
        headings: list[str] = []
        node = table
        while node is not None:
            node = node.previous_sibling
            if not isinstance(node, Tag):
                continue

            heading_tag = None
            if node.name in {"h2", "h3", "h4", "h5"}:
                heading_tag = node
            elif "mw-heading" in (node.get("class") or []):
                heading_tag = node.find(["h2", "h3", "h4", "h5"], recursive=False)

            if heading_tag is None:
                continue

            text = self._clean_text(heading_tag.get_text(" ", strip=True))
            if text:
                headings.append(text)
            if heading_tag.name == "h2":
                break

        headings.reverse()
        return headings
