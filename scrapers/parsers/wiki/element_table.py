from bs4 import Tag

from models.data.parsed.html_elements import TableElementData
from scrapers.parsers.html_elements.table import TableElementParser


class WikiTableElementParser(TableElementParser):
    """Wikipedia HTML element parser for `<table class=\"wikitable\">`."""

    def parse(self, raw: Tag) -> TableElementData:
        return super().parse(raw)
