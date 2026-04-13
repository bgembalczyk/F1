from __future__ import annotations

from dataclasses import dataclass

from scrapers.parsers.section.assembler import SectionAssembler
from scrapers.parsers.section.locator import SectionLocator
from scrapers.parsers.wiki.element import ElementRegistry
from scrapers.parsers.wiki.element import WikiElementSet
from scrapers.parsers.wiki.element import build_wikipedia_element_registry
from scrapers.parsers.wiki.element_factory import build_default_wiki_element_parsers


@dataclass(frozen=True)
class SectionParsingToolbox:
    """Narzędzia parsera sekcji: extract/parse (bez translacji domenowej)."""

    element_parsers: WikiElementSet
    element_registry: ElementRegistry
    section_locator: SectionLocator
    section_assembler: SectionAssembler


def build_default_section_toolbox() -> SectionParsingToolbox:
    element_parsers = build_default_wiki_element_parsers()
    return SectionParsingToolbox(
        element_parsers=element_parsers,
        element_registry=build_wikipedia_element_registry(parsers=element_parsers),
        section_locator=SectionLocator(),
        section_assembler=SectionAssembler(),
    )


SectionParserToolbox = SectionParsingToolbox


__all__ = [
    "SectionParsingToolbox",
    "SectionParserToolbox",
    "build_default_section_toolbox",
]
