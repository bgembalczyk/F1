from __future__ import annotations

from warnings import warn

from .base_extractor import BaseInfoboxExtractor
from .base_extractor import DefaultInfoboxExtractor

warn(
    "scrapers.infobox.extraction.extractor.base is deprecated; use "
    "scrapers.infobox.extraction.extractor.base_extractor",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["BaseInfoboxExtractor", "DefaultInfoboxExtractor"]
