from __future__ import annotations

from dataclasses import dataclass

from scrapers.parsers.wiki.list import ListParser
from scrapers.parsers.table.wiki.table import WikiTableHtmlParser
from scrapers.parsers.wiki.figure import FigureParser
from scrapers.infobox.parsers.html import WikiInfoboxHtmlParser
from scrapers.parsers.wiki.navbox import NavBoxParser
from scrapers.parsers.wiki.paragraph import ParagraphParser
from scrapers.parsers.wiki.references_wrap import ReferencesWrapParser


@dataclass(frozen=True)
class WikiElementParsers:
    infobox_parser: WikiInfoboxHtmlParser
    paragraph_parser: ParagraphParser
    figure_parser: FigureParser
    list_parser: ListParser
    table_parser: WikiTableHtmlParser
    navbox_parser: NavBoxParser
    references_wrap_parser: ReferencesWrapParser


def build_default_wiki_element_parsers() -> WikiElementParsers:
    return WikiElementParsers(
        infobox_parser=WikiInfoboxHtmlParser(),
        paragraph_parser=ParagraphParser(),
        figure_parser=FigureParser(),
        list_parser=ListParser(),
        table_parser=WikiTableHtmlParser(),
        navbox_parser=NavBoxParser(),
        references_wrap_parser=ReferencesWrapParser(),
    )
