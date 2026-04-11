from __future__ import annotations

from dataclasses import dataclass

from scrapers.parsers.wiki.list import ListParser
from scrapers.parsers.table.wiki.table import WikiTableParser
from scrapers.parsers.wiki.figure import FigureParser
from scrapers.parsers.wiki.infobox import InfoboxParser
from scrapers.parsers.wiki.navbox import NavBoxParser
from scrapers.parsers.wiki.paragraph import ParagraphParser
from scrapers.parsers.wiki.references_wrap import ReferencesWrapParser


@dataclass(frozen=True)
class WikiElementParsers:
    infobox_parser: InfoboxParser
    paragraph_parser: ParagraphParser
    figure_parser: FigureParser
    list_parser: ListParser
    table_parser: WikiTableParser
    navbox_parser: NavBoxParser
    references_wrap_parser: ReferencesWrapParser


def build_default_wiki_element_parsers() -> WikiElementParsers:
    return WikiElementParsers(
        infobox_parser=InfoboxParser(),
        paragraph_parser=ParagraphParser(),
        figure_parser=FigureParser(),
        list_parser=ListParser(),
        table_parser=WikiTableParser(),
        navbox_parser=NavBoxParser(),
        references_wrap_parser=ReferencesWrapParser(),
    )
