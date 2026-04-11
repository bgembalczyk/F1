from __future__ import annotations

from dataclasses import dataclass

from scrapers.parsers.section.wiki.assembler import SectionAssembler
from scrapers.parsers.section.wiki.locator import SectionLocator
from scrapers.parsers.wiki.element import WikiElementParsers
from scrapers.parsers.wiki.element import build_wikipedia_element_registry
from scrapers.parsers.wiki.element import build_default_wiki_element_parsers
from scrapers.parsers.wiki.element import ElementParserRegistry
from scrapers.parsers.wiki.domain_mapper import DomainMapper
from scrapers.parsers.wiki.domain_mapper import build_default_domain_mapper


@dataclass(frozen=True)
class SectionParserToolbox:
    """Narzędzia dobierane przez parser sekcji.

    Sekcja jest punktem wejścia dla użytkownika końcowego, więc to parser sekcji
    decyduje jakich parserów elementarnych użyć do parsowania HTML wewnątrz sekcji.
    """

    element_parsers: WikiElementParsers
    element_registry: ElementParserRegistry
    section_locator: SectionLocator
    section_assembler: SectionAssembler
    domain_mapper: DomainMapper


def build_default_section_toolbox() -> SectionParserToolbox:
    element_parsers = build_default_wiki_element_parsers()
    return SectionParserToolbox(
        element_parsers=element_parsers,
        element_registry=build_wikipedia_element_registry(parsers=element_parsers),
        section_locator=SectionLocator(),
        section_assembler=SectionAssembler(),
        domain_mapper=build_default_domain_mapper(),
    )


__all__ = ["SectionParserToolbox", "build_default_section_toolbox"]
