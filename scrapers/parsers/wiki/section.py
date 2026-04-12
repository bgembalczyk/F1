from models.data.parsed.html_elements import SectionElementData
from scrapers.parsers.wiki.elements.section_element_parser import WikiSectionElementParser
from scrapers.parsers.wiki.elements.abc import WikiSectionHtmlParserABC


class DefaultWikiSectionParser(WikiSectionHtmlParserABC, WikiSectionElementParser):
    """Wiki parser for article section containers."""


__all__ = ["DefaultWikiSectionParser", "SectionElementData"]
