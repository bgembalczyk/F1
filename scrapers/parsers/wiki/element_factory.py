from scrapers.parsers.wiki.element import ElementRegistry
from scrapers.parsers.wiki.element import WikiElementSet
from scrapers.parsers.wiki.element import build_wikipedia_element_registry
from scrapers.parsers.figure_element_parser import FigureElementParser
from scrapers.parsers.infobox.wiki_html import WikiInfoboxHtmlParser
from scrapers.parsers.navbox_element_parser import NavboxElementParser
from scrapers.parsers.paragraph_element_parser import ParagraphElementParser
from scrapers.parsers.wiki.table import WikiTableParser
from scrapers.parsers.wiki.element_references import WikiReferencesElementParser
from scrapers.parsers.list_element_parser import ListElementParser


def build_default_wiki_element_parsers() -> WikiElementSet:
    return WikiElementSet(
        infobox_parser=WikiInfoboxHtmlParser(),
        paragraph_parser=ParagraphElementParser(),
        figure_parser=FigureElementParser(),
        list_parser=ListElementParser(),
        table_parser=WikiTableParser(),
        navbox_parser=NavboxElementParser(),
        references_parser=WikiReferencesElementParser(),
    )


def build_default_wikipedia_element_registry() -> ElementRegistry:
    return build_wikipedia_element_registry(
        parsers=build_default_wiki_element_parsers(),
    )


__all__ = [
    "build_default_wiki_element_parsers",
    "build_default_wikipedia_element_registry",
]
