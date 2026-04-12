from __future__ import annotations

from scrapers.parsers.roles import SectionParserABC

# Canonical section parser contract used across scrapers.
SectionParserProtocol = SectionParserABC

__all__ = ["SectionParserABC", "SectionParserProtocol"]
