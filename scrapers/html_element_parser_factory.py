from scrapers.adapters.html_elements import HtmlElementAdapterSet
from scrapers.parsers.html_elements.figure import FigureElementParser
from scrapers.parsers.html_elements.infobox import InfoboxElementParser
from scrapers.parsers.html_elements.list import ListElementParser
from scrapers.parsers.html_elements.navbox import NavboxElementParser
from scrapers.parsers.html_elements.paragraph import ParagraphElementParser
from scrapers.parsers.html_elements.table import TableElementParser
from scrapers.parsers.wiki.references_wrap import ReferencesWrapParser


class HtmlElementBuilder:
    def build(self) -> HtmlElementAdapterSet:
        return HtmlElementAdapterSet(
            infobox_parser=InfoboxElementParser(),
            paragraph_parser=ParagraphElementParser(),
            figure_parser=FigureElementParser(),
            list_parser=ListElementParser(),
            table_parser=TableElementParser(),
            navbox_parser=NavboxElementParser(),
            references_wrap_parser=ReferencesWrapParser(),
        )


# Backward-compatible alias
HtmlElementParserFactory = HtmlElementBuilder
HtmlElementParserBuilder = HtmlElementBuilder
