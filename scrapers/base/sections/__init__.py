"""Public exports for section parsing abstractions.

Keep this module free of eager imports to avoid circular dependencies between
``scrapers.base.helpers`` and section adapters.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .adapter import SectionAdapter
    from .adapter import SectionAdapterEntry
    from .critical_sections import CriticalSection
    from .critical_sections import DOMAIN_CRITICAL_SECTIONS
    from .interface import SectionParseResult
    from .interface import SectionParser
    from .interface import SectionTableParser
    from .interface import SectionTextParser

__all__ = [
    "SectionAdapter",
    "SectionAdapterEntry",
    "CriticalSection",
    "DOMAIN_CRITICAL_SECTIONS",
    "SectionParseResult",
    "SectionParser",
    "SectionTableParser",
    "SectionTextParser",
]


def __getattr__(name: str):
    if name in {"SectionAdapter", "SectionAdapterEntry"}:
        from .adapter import SectionAdapter, SectionAdapterEntry

        return {
            "SectionAdapter": SectionAdapter,
            "SectionAdapterEntry": SectionAdapterEntry,
        }[name]
    if name in {"CriticalSection", "DOMAIN_CRITICAL_SECTIONS"}:
        from .critical_sections import CriticalSection, DOMAIN_CRITICAL_SECTIONS

        return {
            "CriticalSection": CriticalSection,
            "DOMAIN_CRITICAL_SECTIONS": DOMAIN_CRITICAL_SECTIONS,
        }[name]
    if name in {
        "SectionParseResult",
        "SectionParser",
        "SectionTableParser",
        "SectionTextParser",
    }:
        from .interface import (
            SectionParseResult,
            SectionParser,
            SectionTableParser,
            SectionTextParser,
        )

        return {
            "SectionParseResult": SectionParseResult,
            "SectionParser": SectionParser,
            "SectionTableParser": SectionTableParser,
            "SectionTextParser": SectionTextParser,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
