from scrapers.parsers.list.wiki import ListParser as _ListParser


class WikiListParser(_ListParser):
    """Wiki parser for list elements (<ul>/<ol>)."""


# Backward-compatible alias.
ListParser = WikiListParser

__all__ = ["WikiListParser", "ListParser"]
