from scrapers.parsers.wiki.base import WikiListParser
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
        infobox_parser=WikiInfoboxParser(),
        paragraph_parser=WikiParagraphParser(),
        figure_parser=WikiFigureParser(),
        list_parser=WikiListParser(),
        table_parser=WikiTableParser(),
        navbox_parser=WikiNavboxParser(),
        references_wrap_parser=ReferencesWrapParser(),
    )


def build_default_wikipedia_element_registry() -> ElementRegistry:
    return build_wikipedia_element_registry(
        parsers=build_default_wiki_element_parsers()
    )


__all__ = [
    "build_default_wiki_element_parsers",
    "build_default_wikipedia_element_registry",
]
