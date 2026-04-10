from __future__ import annotations

from dataclasses import dataclass

from scrapers.parsers.figure import FigureParser
from scrapers.parsers.infobox import InfoboxParser
from scrapers.parsers.list.wiki import ListParser
from scrapers.parsers.navbox import NavBoxParser
from scrapers.parsers.paragraph import ParagraphParser
from scrapers.parsers.references_wrap import ReferencesWrapParser
from scrapers.parsers.table.wiki.table import WikiTableParser


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
