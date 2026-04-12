"""Wiki table parsers package.

``WikiTableParser`` is the canonical concrete entry-point for parsing
``<table class="wikitable">`` elements from Wikipedia articles.
``TableParser`` is the stable public short-name alias.
"""

from scrapers.parsers.wiki.table.html import WikiTableHtmlParser


class WikiTableParser(WikiTableHtmlParser):
    """Concrete wiki table parser – delegates to ``WikiTableHtmlParser``.

    This class is the stable public name for the wiki table parsing layer.
    It takes a ``bs4.Tag`` (``<table>``) and returns a structured ``dict``
    with keys ``headers``, ``rows``, ``raw_rows`` and ``rich_rows``.
    """


# ``TableParser`` is the canonical short public name for this parser.
TableParser = WikiTableParser


__all__ = ["TableParser", "WikiTableParser"]
