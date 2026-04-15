from scrapers.adapters.html_elements import HtmlElementAdapterSet
from scrapers.parsers.figure_element_parser import FigureElementParser
from scrapers.parsers.wiki.table import WikiTableParser
from scrapers.parsers.infobox.wiki_html import WikiInfoboxHtmlParser
from scrapers.parsers.list_element_parser import ListElementParser
from scrapers.parsers.navbox_element_parser import NavboxElementParser
from scrapers.parsers.paragraph_element_parser import ParagraphElementParser
from scrapers.parsers.wiki.element_references import WikiReferencesElementParser


class HtmlElementBuilder:
    def build(self) -> HtmlElementAdapterSet:
        return HtmlElementAdapterSet(
            infobox_parser=WikiInfoboxHtmlParser(),
            paragraph_parser=ParagraphElementParser(),
            figure_parser=FigureElementParser(),
            list_parser=ListElementParser(),
            table_html_parser=WikiTableParser(),
            navbox_parser=NavboxElementParser(),
            references_wrap_parser=WikiReferencesElementParser(),
        )
