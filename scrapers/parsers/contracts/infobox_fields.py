"""Canonical infobox field parser contracts (ABCs).

These re-exports keep infobox-field parser contracts colocated with other parser
contracts under ``scrapers.parsers.contracts``.
"""

from scrapers.parsers.infobox_parser_abc import InfoboxHtmlFieldParserABC
from scrapers.parsers.infobox_parser_abc import InfoboxRowsParserABC

__all__ = [
    "InfoboxHtmlFieldParserABC",
    "InfoboxRowsParserABC",
]
