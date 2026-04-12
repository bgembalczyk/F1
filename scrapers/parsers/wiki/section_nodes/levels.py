from __future__ import annotations

from abc import ABC

from scrapers.parsers.section_parser_abc import NestedSectionParserABC


class SubSectionLevelMixin(ABC):
    """Marker mixin for subsection-level parsers (h4 scope)."""


class SubSubSectionLevelMixin(SubSectionLevelMixin, ABC):
    """Marker mixin for sub-subsection-level parsers (h5 scope)."""


class WikiSubSectionParserABC(SubSectionLevelMixin, NestedSectionParserABC, ABC):
    """Contract for subsection parser nodes."""


class WikiSubSubSectionParserABC(SubSubSectionLevelMixin, WikiSubSectionParserABC, ABC):
    """Contract for sub-subsection parser nodes."""


__all__ = [
    "SubSectionLevelMixin",
    "SubSubSectionLevelMixin",
    "WikiSubSectionParserABC",
    "WikiSubSubSectionParserABC",
]
