from scrapers.parsers.wiki.element import ElementParserRegistry
from scrapers.parsers.wiki.element import WikiElementParsers
from scrapers.parsers.wiki.element import build_wikipedia_element_registry
from scrapers.parsers.wiki.figure import WikiFigureParser
from scrapers.parsers.wiki.infobox import WikiInfoboxParser
from scrapers.parsers.wiki.list import WikiListParser
from scrapers.parsers.wiki.navbox import WikiNavboxParser
from scrapers.parsers.wiki.paragraph import WikiParagraphParser
from scrapers.parsers.wiki.references_wrap import ReferencesWrapParser
from scrapers.parsers.wiki.table import WikiTableParser


def build_default_wiki_element_parsers() -> WikiElementParsers:
    return WikiElementParsers(
        infobox_parser=WikiInfoboxParser(),
        paragraph_parser=WikiParagraphParser(),
        figure_parser=WikiFigureParser(),
        list_parser=WikiListParser(),
        table_parser=WikiTableParser(),
        navbox_parser=WikiNavboxParser(),
        references_wrap_parser=ReferencesWrapParser(),
    )


def build_default_wikipedia_element_registry() -> ElementParserRegistry:
    return build_wikipedia_element_registry(
        parsers=build_default_wiki_element_parsers()
    )


__all__ = [
    "build_default_wiki_element_parsers",
    "build_default_wikipedia_element_registry",
]
