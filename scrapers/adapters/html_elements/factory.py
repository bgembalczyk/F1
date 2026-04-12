from __future__ import annotations

from dataclasses import dataclass

from scrapers.parsers.figure_element_parser import FigureElementParser
from scrapers.parsers.infobox_element_parser import InfoboxElementParser
from scrapers.parsers.list_element_parser import ListElementParser
from scrapers.parsers.navbox_element_parser import NavboxElementParser
from scrapers.parsers.paragraph_element_parser import ParagraphElementParser
from scrapers.parsers.table_element_parser import TableElementParser
from scrapers.parsers.wiki.references_wrap import ReferencesWrapParser


@dataclass(frozen=True)
class HtmlElementAdapterSet:
    infobox_parser: InfoboxElementParser
    paragraph_parser: ParagraphElementParser
    figure_parser: FigureElementParser
    list_parser: ListElementParser
    table_html_parser: TableElementParser
    navbox_parser: NavboxElementParser
    references_wrap_parser: ReferencesWrapParser
