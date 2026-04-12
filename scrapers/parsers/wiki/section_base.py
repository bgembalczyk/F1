from abc import ABC

from scrapers.parsers.soup_parser_abc import HtmlSoupParserABC
from scrapers.parsers.wiki.base import WikiRecords


class WikiSectionParserBase(HtmlSoupParserABC[WikiRecords], ABC):
    """Kontrakt parserów sekcji artykułów Wikipedii."""
