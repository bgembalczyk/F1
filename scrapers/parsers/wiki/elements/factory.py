from scrapers.parsers.wiki.base import WikiListParser
from scrapers.parsers.wiki.elements.registry import ElementRegistry
from scrapers.parsers.wiki.elements.registry import WikiElementSet
from scrapers.parsers.wiki.elements.registry import build_wikipedia_element_registry
from scrapers.parsers.wiki.elements.figure_element_parser import WikiFigureElementParser
from scrapers.parsers.wiki.elements.infobox_element_parser import WikiInfoboxElementParser
from scrapers.parsers.wiki.elements.list_element_parser import WikiListElementParser
from scrapers.parsers.wiki.elements.navbox_element_parser import WikiNavboxElementParser
from scrapers.parsers.wiki.elements.paragraph_element_parser import WikiParagraphElementParser
from scrapers.parsers.wiki.elements.references_element_parser import WikiReferencesElementParser
from scrapers.parsers.wiki.elements.table_element_parser import WikiTableElementParser


def build_default_wiki_element_parsers() -> WikiElementSet:
    return WikiElementSet(
        infobox_parser=WikiInfoboxElementParser(),
        paragraph_parser=WikiParagraphElementParser(),
        figure_parser=WikiFigureElementParser(),
        list_parser=WikiListElementParser(),
        table_parser=WikiTableElementParser(),
        navbox_parser=WikiNavboxElementParser(),
        references_wrap_parser=WikiReferencesElementParser(),
        references_parser=WikiReferencesElementParser(),
    )


def build_default_wikipedia_element_registry() -> ElementRegistry:
    return build_wikipedia_element_registry(
        parsers=build_default_wiki_element_parsers()
    )


__all__ = [
    "build_default_wiki_element_parsers",
    "build_default_wikipedia_element_registry",
]
