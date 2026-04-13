from scrapers.parsers.contracts.mapping import WikiElementClassifierABC
from scrapers.parsers.contracts.wiki_elements import WikiFigureElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiInfoboxElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiListElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiNavboxElementParserABC
from scrapers.parsers.contracts.wiki_elements import WikiTableElementParserABC

__all__ = [
    "WikiTableElementParserABC",
    "WikiNavboxElementParserABC",
    "WikiListElementParserABC",
    "WikiInfoboxElementParserABC",
    "WikiFigureElementParserABC",
    "WikiElementClassifierABC",
]
