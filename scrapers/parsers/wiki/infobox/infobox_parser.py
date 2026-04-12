from models.data.parsed.infobox import InfoboxParsedData
from scrapers.parsers.infobox.wiki_html import WikiInfoboxElementParserBase
from scrapers.parsers.infobox.wiki_html import WikiInfoboxHtmlParser
from scrapers.parsers.wiki.elements.abc import WikiInfoboxHtmlParserABC


class WikiInfoboxParser(WikiInfoboxHtmlParserABC, WikiInfoboxHtmlParser):
    """Wiki parser for infobox tables (<table class="infobox">)."""


__all__ = [
    "WikiInfoboxElementParserBase",
    "WikiInfoboxParser",
    "InfoboxParsedData",
]
