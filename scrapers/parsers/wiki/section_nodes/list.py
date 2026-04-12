from __future__ import annotations

from abc import ABC

from bs4 import Tag

from models.data.wiki.list import WikiListData
from scrapers.parsers.element_parser_abc import ListElementParserABC
from scrapers.parsers.wiki.section_nodes.base import WikiNodeParserABC
from scrapers.parsers.wiki.section_nodes.section import WikiSectionParserABC


class WikiListSectionParserABC(
    WikiSectionParserABC,
    WikiNodeParserABC[Tag, WikiListData],
    ListElementParserABC[WikiListData],
    ABC,
):
    """Contract for list-node parsers (<ul>/<ol>) used inside wiki sections."""


__all__ = ["WikiListSectionParserABC", "WikiListParserABC"]


WikiListParserABC = WikiListSectionParserABC
