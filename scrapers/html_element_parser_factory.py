from scrapers.adapters.html_elements import HtmlElementParserAdapterSet
from scrapers.parsers.wiki.element_figure import WikiFigureElementParser
from scrapers.parsers.wiki.element_infobox import WikiInfoboxElementParser
from scrapers.parsers.wiki.element_list import WikiListElementParser
from scrapers.parsers.wiki.element_navbox import WikiNavboxElementParser
from scrapers.parsers.wiki.element_paragraph import WikiParagraphElementParser
from scrapers.parsers.wiki.element_references import WikiReferencesElementParser
from scrapers.parsers.wiki.element_table import WikiTableElementParser


class HtmlElementParserBuilder:
    def build(self) -> HtmlElementParserAdapterSet:
        return HtmlElementParserAdapterSet(
            infobox_parser=WikiInfoboxElementParser(),
            paragraph_parser=WikiParagraphElementParser(),
            figure_parser=WikiFigureElementParser(),
            list_parser=WikiListElementParser(),
            table_parser=WikiTableElementParser(),
            navbox_parser=WikiNavboxElementParser(),
            references_wrap_parser=WikiReferencesElementParser(),
        )


# Backward-compatible alias
HtmlElementParserFactory = HtmlElementParserBuilder
