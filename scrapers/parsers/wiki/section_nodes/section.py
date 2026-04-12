from __future__ import annotations

from abc import ABC

from bs4 import BeautifulSoup

from models.data.wiki.section import WikiSectionData
from scrapers.parsers.element_parser_abc import SectionElementParserABC
from scrapers.parsers.parser_abc import ParserABC
from scrapers.parsers.wiki.section_nodes.base import WikiNodeParserABC


class WikiSectionParserABC(
    WikiNodeParserABC[BeautifulSoup, WikiSectionData],
    SectionElementParserABC[WikiSectionData],
    ParserABC[BeautifulSoup, WikiSectionData],
    ABC,
):
    """Canonical parser contract for wiki section content blocks (h2/h3 + children)."""


__all__ = ["WikiSectionParserABC"]
