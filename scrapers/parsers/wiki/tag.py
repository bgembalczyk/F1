from abc import ABC
from typing import Generic

from scrapers.parsers.tag_parser_abc import HtmlTagParserABC
from scrapers.parsers.wiki.base import TWikiOutput


class WikiTagParser(HtmlTagParserABC[TWikiOutput], ABC, Generic[TWikiOutput]):
    """Kontrakt parserów pojedynczych tagów HTML Wikipedii."""
