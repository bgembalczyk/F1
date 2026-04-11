from __future__ import annotations

from dataclasses import dataclass

from scrapers.parsers.wiki.element import WikiElementParsers
from scrapers.parsers.wiki.element import build_default_wiki_element_parsers


@dataclass(frozen=True)
class SectionParserToolbox:
    """Narzędzia dobierane przez parser sekcji.

    Sekcja jest punktem wejścia dla użytkownika końcowego, więc to parser sekcji
    decyduje jakich parserów elementarnych użyć do parsowania HTML wewnątrz sekcji.
    """

    element_parsers: WikiElementParsers


def build_default_section_toolbox() -> SectionParserToolbox:
    return SectionParserToolbox(
        element_parsers=build_default_wiki_element_parsers(),
    )


__all__ = ["SectionParserToolbox", "build_default_section_toolbox"]
