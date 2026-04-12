from abc import ABC

from scrapers.parsers.element_parser_abc import HtmlSoupParserABC
from scrapers.parsers.wiki.base import WikiRecords


class WikiTableElementParserBase(HtmlSoupParserABC[WikiRecords], ABC):
    """Kontrakt parserów tabel Wikipedii."""
