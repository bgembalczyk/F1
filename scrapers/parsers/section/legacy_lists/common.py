from __future__ import annotations

from dataclasses import replace

from scrapers.parsers.section.toolbox import SectionParserToolbox
from scrapers.parsers.wiki.element import ElementRegistry
from scrapers.parsers.wiki.element import WikiElementSet


def with_toolbox_overrides(
    toolbox: SectionParserToolbox | None,
    *,
    element_parsers: WikiElementSet | None = None,
    element_registry: ElementRegistry | None = None,
) -> SectionParserToolbox | None:
    """Build a parser toolbox with optional element-level overrides."""
    if toolbox is None:
        return None
    if element_parsers is None and element_registry is None:
        return toolbox
    return replace(
        toolbox,
        element_parsers=element_parsers or toolbox.element_parsers,
        element_registry=element_registry or toolbox.element_registry,
    )


__all__ = ["with_toolbox_overrides"]
