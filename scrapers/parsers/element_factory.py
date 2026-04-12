from scrapers.adapters.html_elements import HtmlElementAdapterSet
from scrapers.parsers.html_elements.figure_element_parser import FigureElementParser
from scrapers.parsers.html_elements.infobox_element_parser import InfoboxElementParser
from scrapers.parsers.html_elements.list_element_parser import ListElementParser
from scrapers.parsers.html_elements.navbox_element_parser import NavboxElementParser
from scrapers.parsers.html_elements.paragraph_element_parser import ParagraphElementParser
from scrapers.parsers.html_elements.table_element_parser import TableElementParser
from scrapers.parsers.wiki.references_wrap import ReferencesWrapParser


class HtmlElementBuilder:
    def build(self) -> HtmlElementAdapterSet:
        return HtmlElementAdapterSet(
            infobox_parser=InfoboxElementParser(),
            paragraph_parser=ParagraphElementParser(),
            figure_parser=FigureElementParser(),
            list_parser=ListElementParser(),
            table_html_parser=TableElementParser(),
            navbox_parser=NavboxElementParser(),
            references_wrap_parser=ReferencesWrapParser(),
        )
