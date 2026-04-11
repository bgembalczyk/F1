from bs4 import Tag

from models.data.parsed.html_elements import TableElementData
from scrapers.parsers.html_elements.table import TableElementParser
from scrapers.parsers.wiki.families import WikiTableHtmlParserABC


class WikiTableElementParser(WikiTableHtmlParserABC, TableElementParser):
    """Wikipedia HTML element parser for `<table class=\"wikitable\">`."""

    def parse(self, raw: Tag) -> TableElementData:
        return super().parse(raw)
