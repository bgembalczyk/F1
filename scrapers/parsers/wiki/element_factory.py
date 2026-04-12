from scrapers.parsers.wiki.element import ElementRegistry
from scrapers.parsers.wiki.element import WikiElementSet
from scrapers.parsers.wiki.element import build_wikipedia_element_registry
from scrapers.parsers.wiki.element_figure import WikiFigureElementParser
from scrapers.parsers.wiki.element_infobox import WikiInfoboxElementParser
from scrapers.parsers.wiki.element_list import WikiListElementParser
from scrapers.parsers.wiki.element_navbox import WikiNavboxElementParser
from scrapers.parsers.wiki.element_paragraph import WikiParagraphElementParser
from scrapers.parsers.wiki.element_references import WikiReferencesElementParser
from scrapers.parsers.wiki.element_table import WikiTableElementParser


def build_default_wiki_element_parsers() -> WikiElementSet:
    return WikiElementSet(
        infobox_parser=WikiInfoboxElementParser(),
        paragraph_parser=WikiParagraphElementParser(),
        figure_parser=WikiFigureElementParser(),
        list_parser=WikiListElementParser(),
        table_parser=WikiTableElementParser(),
        navbox_parser=WikiNavboxElementParser(),
        references_parser=WikiReferencesElementParser(),
    )


def build_default_wikipedia_element_registry() -> ElementRegistry:
    return build_wikipedia_element_registry(parsers=build_default_wiki_element_parsers())


__all__ = [
    "build_default_wiki_element_parsers",
    "build_default_wikipedia_element_registry",
]
