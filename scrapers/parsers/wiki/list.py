from abc import ABC

from scrapers.parsers.tag_parser_abc import TagParserABC
from scrapers.parsers.wiki.base import WikiRecords


class WikiListParser(TagParserABC[WikiRecords], ABC):
    """Kontrakt parserów list Wikipedii (np. <ul>/<ol>)."""
