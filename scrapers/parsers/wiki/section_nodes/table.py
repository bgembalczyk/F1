from __future__ import annotations

from abc import ABC

from bs4 import Tag

from models.data.wiki.table import WikiTableData
from scrapers.parsers.element_parser_abc import TableElementParserABC
from scrapers.parsers.wiki.section_nodes.base import WikiNodeParserABC
from scrapers.parsers.wiki.section_nodes.section import WikiSectionParserABC


class WikiTableSectionParserABC(
    WikiSectionParserABC,
    WikiNodeParserABC[Tag, WikiTableData],
    TableElementParserABC[WikiTableData],
    ABC,
):
    """Contract for table-node parsers (<table>) used inside wiki sections."""


__all__ = ["WikiTableSectionParserABC", "WikiTableParserABC"]


WikiTableParserABC = WikiTableSectionParserABC
