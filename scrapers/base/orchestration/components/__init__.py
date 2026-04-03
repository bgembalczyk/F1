"""Public API for orchestration components.

Konwencja: każdy nowy komponent dodajemy do ``__init__.py`` i do ``__all__``.
"""

from scrapers.base.orchestration.components.section_source_adapter import (
    SectionSourceAdapter,
)

__all__ = ["SectionSourceAdapter"]
