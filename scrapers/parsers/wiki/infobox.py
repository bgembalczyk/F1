from models.data.parsed.infobox import InfoboxParsedData
from scrapers.parsers.infobox.wiki_html import WikiInfoboxElementParserBase
from scrapers.parsers.infobox.wiki_html import WikiInfoboxHtmlParser


class WikiInfoboxParser(WikiInfoboxHtmlParser):
    """Wiki parser for infobox tables (<table class=\"infobox\">)."""


# Backward-compatible alias.
InfoboxParser = WikiInfoboxParser

__all__ = [
    "WikiInfoboxElementParserBase",
    "WikiInfoboxParser",
    "InfoboxParser",
    "InfoboxParsedData",
]
