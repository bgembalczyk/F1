from __future__ import annotations

from typing import Any

from scrapers.assemblers.assembler_abc import AssemblerABC
from scrapers.parsers.input_adapters import as_table_fragments
from scrapers.parsers.input_types import WikiParserInput
from scrapers.parsers.wiki.table.article import ArticleTablesParser
from scrapers.parsers.wiki.table.base import WikiTableBaseMapper
from scrapers.parsers.wiki.table.mapped.lap_records_wiki_table_mapper import (
    LapRecordsWikiTableMapper,
)
from scrapers.parsers.wiki.table.mapped.race_results_table_mapper import (
    RaceResultsTableMapper,
)
from scrapers.parsers.wiki.table.mapped.standings_table_mapper import (
    StandingsTableMapper,
)


class ArticleTablesAssembler(AssemblerABC):
    """Assembler tabel artykułu: parser HTML + mapowanie domenowe."""

    def __init__(
        self,
        *,
        html_parser: ArticleTablesParser | None = None,
        specialized_mappers: list[WikiTableBaseMapper] | None = None,
    ) -> None:
        self._html_parser = html_parser or ArticleTablesParser()
        self._specialized_mappers = specialized_mappers or [
            StandingsTableMapper(),
            RaceResultsTableMapper(),
            LapRecordsWikiTableMapper(),
        ]

    def assemble(self, element: WikiParserInput) -> list[dict[str, Any]]:
        dict_fragments = as_table_fragments(element)
        if dict_fragments:
            return dict_fragments

        parsed_tables = self._html_parser.parse(element)
        return [self._assemble_table(table) for table in parsed_tables]

    def _assemble_table(self, table_data: dict[str, Any]) -> dict[str, Any]:
        for mapper in self._specialized_mappers:
            specialized = mapper.map(table_data)
            if specialized is not None:
                return specialized

        fallback = dict(table_data)
        fallback["table_type"] = "wiki_table"
        return fallback


__all__ = ["ArticleTablesAssembler"]
