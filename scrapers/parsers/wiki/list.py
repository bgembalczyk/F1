from abc import ABC

from scrapers.parsers.tag_parser_abc import HtmlTagParserABC
from scrapers.parsers.wiki.base import WikiRecords


class WikiListParser(HtmlTagParserABC[WikiRecords], ABC):
    """Kontrakt parserów list Wikipedii (np. <ul>/<ol>)."""
