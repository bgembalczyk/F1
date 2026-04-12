from abc import ABC
from typing import Generic

from scrapers.parsers.tag_parser_abc import TagParserABC
from scrapers.parsers.wiki.base import TWikiOutput


class WikiTagParser(TagParserABC[TWikiOutput], ABC, Generic[TWikiOutput]):
    """Kontrakt parserów pojedynczych tagów HTML Wikipedii."""
