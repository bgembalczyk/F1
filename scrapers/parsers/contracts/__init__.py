from scrapers.parsers.contracts.mapping import WikiElementClassifierABC
from scrapers.parsers.contracts.wiki_elements import WikiFigureElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiInfoboxElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiListElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiNavboxElementParserABC

__all__ = [
    "WikiNavboxElementParserABC",
    "WikiListElementParserABC",
    "WikiInfoboxElementParserABC",
    "WikiFigureElementParserABC",
    "WikiElementClassifierABC",
]
