from models.data.parsed.html_elements import SectionElementData
from scrapers.parsers.html_elements.section import SectionElementParser


class WikiSectionParser(SectionElementParser):
    """Wiki parser for article section containers."""


__all__ = ["WikiSectionParser", "SectionElementData"]
