from __future__ import annotations

from typing import Any

from bs4 import Tag

from scrapers.helpers.text import clean_wiki_text
from scrapers.parsers.html_table import HtmlTableParser
from scrapers.input_adapters import as_table_fragments
from scrapers.input_types import WikiParserInput
from scrapers.parsers.wiki.table.article_tables_parser_abc import ArticleTablesParserABC
from scrapers.parsers.wiki.table.mapped.lap_records_wiki_table_mapper import (
    LapRecordsWikiTableMapper,
)
from scrapers.parsers.wiki.table.mapped.mapped_wiki_table_mapper import MappedWikiTableMapper
from scrapers.parsers.wiki.table.mapped.race_results_table_mapper import RaceResultsTableMapper
from scrapers.parsers.wiki.table.mapped.standings_table_mapper import StandingsTableMapper


class ArticleTablesParser(ArticleTablesParserABC):
    """Wspólny parser tabel wikitable z artykułów Wikipedii."""

    def __init__(
        self,
        *,
        include_heading_path: bool = False,
        include_source_table: bool = False,
        specialized_mappers: list[MappedWikiTableMapper] | None = None,
    ) -> None:
        self.include_heading_path = include_heading_path
        self.include_source_table = include_source_table
        self._html_table_parser = HtmlTableParser()
        self._specialized_mappers = specialized_mappers or [
            StandingsTableMapper(),
            RaceResultsTableMapper(),
            LapRecordsWikiTableMapper(),
        ]

    def parse(self, element: WikiParserInput) -> list[dict[str, Any]]:
        dict_fragments = as_table_fragments(element)
        if dict_fragments:
            return dict_fragments

        tables: list[dict[str, Any]] = []
        for table in element.find_all("table", class_="wikitable"):
            parsed = self.parse_table(table)
            if parsed is not None:
                tables.append(parsed)
        return tables

    def parse_table(self, table: Tag) -> dict[str, Any] | None:
        headers, rows = self._parse_with_html_table_parser(table)
        if not headers:
            return None

        filtered_rows = [
            row for row in rows if any(value.strip() for value in row.values())
        ]
        if not filtered_rows:
            return None

        parsed: dict[str, Any] = {
            "headers": headers,
            "rows": filtered_rows,
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

        parsed.update(self._parse_specialized(parsed))

        return parsed

    def _parse_specialized(self, parsed: dict[str, Any]) -> dict[str, Any]:
        for mapper in self._specialized_mappers:
            specialized = mapper.map(parsed)
            if specialized is not None:
                return specialized
        return {"table_type": "wiki_table"}

    def _parse_with_html_table_parser(
        self,
        table: Tag,
    ) -> tuple[list[str], list[dict[str, str]]]:
        try:
            rows = self._html_table_parser.parse_table(table)
        except RuntimeError:
            return [], []

        if not rows:
            return [], []

        normalized_headers = self._normalize_headers(rows[0].headers)
        parsed_rows: list[dict[str, str]] = []
        for row in rows:
            values = [
                self._clean_text(cell.get_text(" ", strip=True)) for cell in row.cells
            ]
            parsed_rows.append(dict(zip(normalized_headers, values, strict=False)))

        return normalized_headers, parsed_rows

    def _normalize_headers(self, headers: list[str]) -> list[str]:
        return [
            self._clean_text(header) for header in headers if self._clean_text(header)
        ]

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
