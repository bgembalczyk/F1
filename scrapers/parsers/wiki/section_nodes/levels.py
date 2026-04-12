from __future__ import annotations

from abc import ABC

from scrapers.parsers.wiki.section_nodes.base import WikiSectionNodeParserABC


class SectionLevelMixin(ABC):
    """Marker mixin for top-level section parsers (h3 scope)."""


class SubSectionLevelMixin(SectionLevelMixin, ABC):
    """Marker mixin for subsection-level parsers (h4 scope)."""


class SubSubSectionLevelMixin(SubSectionLevelMixin, ABC):
    """Marker mixin for sub-subsection-level parsers (h5 scope)."""


class WikiSectionParserABC(SectionLevelMixin, WikiSectionNodeParserABC, ABC):
    """Contract for top-level section node parsers."""


class WikiSubSectionParserABC(SubSectionLevelMixin, WikiSectionNodeParserABC, ABC):
    """Contract for subsection parser nodes."""


class WikiSubSubSectionParserABC(
    SubSubSectionLevelMixin,
    WikiSectionNodeParserABC,
    ABC,
):
    """Contract for sub-subsection parser nodes."""


__all__ = [
    "SectionLevelMixin",
    "SubSectionLevelMixin",
    "SubSubSectionLevelMixin",
    "WikiSectionParserABC",
    "WikiSubSectionParserABC",
    "WikiSubSubSectionParserABC",
]
