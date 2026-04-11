from __future__ import annotations

from scrapers.parsers.roles import TableDomainMapperABC


TableFragmentParserABC = TableDomainMapperABC
TableParserABC = TableFragmentParserABC


__all__ = ["TableFragmentParserABC", "TableParserABC"]
