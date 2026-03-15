from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.context import WikiParserContext
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import _split_into_parts

_HEADING_CLASS = "mw-heading2"


class ContentTextParser(WikiParser):
    """Parser obszaru treści artykułu Wikipedii.

    Przetwarza div z id zawierającym 'content-text' oraz klasą zawierającą
    'body-content'. Dzieli zawartość na sekcje (poziom 2) i deleguje
    ich parsowanie do SectionParser.

    Pierwsza sekcja (przed pierwszym nagłówkiem h2) nosi nazwę "(Top)".
    Pozostałe sekcje są nazywane zgodnie z id nagłówka h2.
    """

    def __init__(self) -> None:
        self.section_parser = SectionParser()

    def parse(self, element: Tag, context: WikiParserContext | None = None) -> dict[str, Any]:
        """Parsuje obszar treści artykułu.

        Dzieli element na sekcje, parsuje każdą z nich
        za pomocą SectionParser.

        Args:
            element: Div z id zawierającym 'content-text' i klasą 'body-content'.

        Returns:
            Słownik z listą sekcji artykułu.
        """
        tags = [c for c in element.children if isinstance(c, Tag)]
        parts = _split_into_parts(tags, _HEADING_CLASS)
        ctx = context or WikiParserContext.empty()
        sections: list[dict[str, Any]] = []
        for name, group_elements in parts:
            child_ctx = ctx.child(section_name=name, heading_id=name if name != "(Top)" else None)
            sections.append(
                {
                    "name": name,
                    **self.section_parser.parse_group(group_elements, context=child_ctx),
                }
            )
        return {"sections": sections}
