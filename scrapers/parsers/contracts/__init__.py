"""Contracts package — canonical parser ABC re-exports.

This package provides stable, named re-export points for all parser ABCs.
Concrete parsers and consumers should import from here instead of the
implementation modules to stay decoupled from internal paths.
"""

from scrapers.parsers.contracts.html_element_parser_abc import HtmlElementParserABC
from scrapers.parsers.contracts.mapper_abc import MapperABC
from scrapers.parsers.contracts.soup_parser_abc import HtmlTagParserABC
from scrapers.parsers.contracts.wiki_elements import WikiFigureParserABC
from scrapers.parsers.contracts.wiki_elements import WikiInfoboxParserABC
from scrapers.parsers.contracts.wiki_elements import WikiListParserABC
from scrapers.parsers.contracts.wiki_elements import WikiNavboxParserABC
from scrapers.parsers.contracts.wiki_elements import WikiSectionParserABC
from scrapers.parsers.contracts.wiki_elements import WikiTableParserABC

__all__ = [
    "HtmlElementParserABC",
    "MapperABC",
    "HtmlTagParserABC",
    "WikiFigureParserABC",
    "WikiInfoboxParserABC",
    "WikiListParserABC",
    "WikiNavboxParserABC",
    "WikiSectionParserABC",
    "WikiTableParserABC",
]
