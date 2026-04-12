from abc import ABC

from scrapers.parsers.soup_parser_abc import HtmlSoupParserABC
from scrapers.parsers.wiki.base import WikiRecords


class WikiTableElementParserBase(HtmlSoupParserABC[WikiRecords], ABC):
    """Kontrakt parserów tabel Wikipedii."""
