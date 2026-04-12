from abc import ABC

from scrapers.parsers.soup_parser_abc import SoupParserABC
from scrapers.parsers.wiki.base import WikiRecords


class WikiTableElementParserBase(SoupParserABC[WikiRecords], ABC):
    """Kontrakt parserów tabel Wikipedii."""
