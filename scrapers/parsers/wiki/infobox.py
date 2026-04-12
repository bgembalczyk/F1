from models.data.parsed.infobox import InfoboxParsedData
from scrapers.parsers.infobox.wiki_html import WikiInfoboxHtmlParser


class WikiInfoboxParser(WikiInfoboxHtmlParser):
    """Wiki parser for infobox tables (<table class="infobox">)."""


__all__ = [
    "WikiInfoboxParser",
    "InfoboxParsedData",
]
