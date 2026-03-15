from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.context import WikiParserContext
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import WikiElementParserMixin
from scrapers.wiki.parsers.sections.sub_sub_sub_section import _split_into_parts

_HEADING_CLASS = "mw-heading3"


class SectionParser(WikiElementParserMixin, WikiParser):
    """Parser sekcji Wikipedii (poziom 2).

    Przetwarza fragment HTML między kolejnymi:
    <div class="mw-heading mw-heading2"><h2 id=...>

    Dzieli zawartość na podsekcje (poziom 3) i deleguje ich parsowanie
    do SubSectionParser. Dodatkowo korzysta z narzędzi elementarnych
    (InfoboxParser, ParagraphParser, FigureParser, ListParser, TableParser,
    NavBoxParser, ReferencesWrapParser).
    """

    def __init__(self) -> None:
        WikiElementParserMixin.__init__(self)
        self.sub_section_parser = SubSectionParser()

    def parse(self, element: Tag, context: WikiParserContext | None = None) -> dict[str, Any]:
        """Parsuje zawartość sekcji.

        Dzieli element na podsekcje, parsuje każdą z nich
        za pomocą SubSectionParser.

        Args:
            element: Kontener zawierający elementy sekcji.

        Returns:
            Słownik z listą podsekcji.
        """
        return self.parse_group(list(element.children), context=context)

    def parse_group(
        self,
        elements: list,
        context: WikiParserContext | None = None,
    ) -> dict[str, Any]:
        """Parsuje grupę elementów HTML.

        Args:
            elements: Lista elementów (potomków kontenera sekcji).

        Returns:
            Słownik z listą podsekcji.
        """
        tags = [c for c in elements if isinstance(c, Tag)]
        parts = _split_into_parts(tags, _HEADING_CLASS)
        ctx = context or WikiParserContext.empty()
        parsed_sections: list[dict[str, Any]] = []
        for name, group_elements in parts:
            child_ctx = ctx.child(section_name=name, heading_id=name if name != "(Top)" else None)
            parsed_sections.append(
                {
                    "name": name,
                    **self.sub_section_parser.parse_group(group_elements, context=child_ctx),
                }
            )
        return {"sub_sections": parsed_sections}
