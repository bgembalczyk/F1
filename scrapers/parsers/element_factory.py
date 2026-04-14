from scrapers.adapters.html_elements import HtmlElementAdapterSet
from scrapers.parsers.figure_element_parser import FigureElementParser
from scrapers.parsers.infobox_element_parser import InfoboxElementParser
from scrapers.parsers.list_element_parser import ListElementParser
from scrapers.parsers.navbox_element_parser import NavboxElementParser
from scrapers.parsers.paragraph_element_parser import ParagraphElementParser
from scrapers.parsers.table_element_parser import TableElementParser
from scrapers.parsers.wiki.element_references import WikiReferencesElementParser


class HtmlElementBuilder:
    def build(self) -> HtmlElementAdapterSet:
        return HtmlElementAdapterSet(
            infobox_parser=InfoboxElementParser(),
            paragraph_parser=ParagraphElementParser(),
            figure_parser=FigureElementParser(),
            list_parser=ListElementParser(),
            table_html_parser=TableElementParser(),
            navbox_parser=NavboxElementParser(),
            references_wrap_parser=WikiReferencesElementParser(),
        )
