"""Backwards-compatible alias for table section-node parser contract."""

from scrapers.parsers.wiki.section_nodes.table import WikiTableSectionParserABC as WikiTableParserABC

__all__ = ["WikiTableParserABC"]
