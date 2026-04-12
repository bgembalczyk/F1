from models.data.parsed.html_elements import SectionElementData
from scrapers.parsers.wiki.element_section import WikiSectionElementParser
from scrapers.parsers.wiki.families import WikiSectionParserABC


class DefaultWikiSectionParser(WikiSectionParserABC, WikiSectionElementParser):
    """Wiki parser for article section containers."""


__all__ = ["DefaultWikiSectionParser", "SectionElementData"]
