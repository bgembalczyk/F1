from __future__ import annotations

from abc import ABC

from bs4 import Tag

from models.data.wiki.infobox import WikiInfoboxData
from scrapers.parsers.element_parser_abc import InfoboxElementParserABC
from scrapers.parsers.infobox_parser_abc import InfoboxParserABC
from scrapers.parsers.wiki.section_nodes.base import WikiNodeParserABC
from scrapers.parsers.wiki.section_nodes.section import WikiSectionParserABC


class WikiInfoboxSectionParserABC(
    WikiSectionParserABC,
    WikiNodeParserABC[Tag, WikiInfoboxData],
    InfoboxParserABC,
    InfoboxElementParserABC[WikiInfoboxData],
    ABC,
):
    """Contract for infobox parsers (<table class='infobox'>)."""


__all__ = ["WikiInfoboxSectionParserABC", "WikiInfoboxParserABC"]


WikiInfoboxParserABC = WikiInfoboxSectionParserABC
