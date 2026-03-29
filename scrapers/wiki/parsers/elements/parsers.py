from __future__ import annotations

from dataclasses import dataclass

from scrapers.wiki.parsers.elements.figure import FigureParser
from scrapers.wiki.parsers.elements.infobox import InfoboxParser
from scrapers.wiki.parsers.elements.list import ListParser
from scrapers.wiki.parsers.elements.navbox import NavBoxParser
from scrapers.wiki.parsers.elements.paragraph import ParagraphParser
from scrapers.wiki.parsers.elements.references_wrap import ReferencesWrapParser
from scrapers.wiki.parsers.elements.table import TableParser


@dataclass(frozen=True)
class WikiElementParsers:
    infobox_parser: InfoboxParser
    paragraph_parser: ParagraphParser
    figure_parser: FigureParser
    list_parser: ListParser
    table_parser: TableParser
    navbox_parser: NavBoxParser
    references_wrap_parser: ReferencesWrapParser


def build_default_wiki_element_parsers() -> WikiElementParsers:
    return WikiElementParsers(
        infobox_parser=InfoboxParser(),
        paragraph_parser=ParagraphParser(),
        figure_parser=FigureParser(),
        list_parser=ListParser(),
        table_parser=TableParser(),
        navbox_parser=NavBoxParser(),
        references_wrap_parser=ReferencesWrapParser(),
    )
