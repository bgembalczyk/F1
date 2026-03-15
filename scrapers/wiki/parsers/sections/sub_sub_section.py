from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.context import WikiParserContext
from scrapers.wiki.parsers.sections.sub_sub_sub_section import SubSubSubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import WikiElementParserMixin
from scrapers.wiki.parsers.sections.sub_sub_sub_section import _split_into_parts

_HEADING_CLASS = "mw-heading5"


class SubSubSectionParser(WikiElementParserMixin, WikiParser):
    """Parser podpodsekcji Wikipedii (poziom 4).

    Przetwarza fragment HTML między kolejnymi:
    <div class="mw-heading mw-heading4"><h4 id=...>

    Dzieli zawartość na podpodpodsekcje (poziom 5) i deleguje ich parsowanie
    do SubSubSubSectionParser. Dodatkowo korzysta z narzędzi elementarnych
    (InfoboxParser, ParagraphParser, FigureParser, ListParser, TableParser,
    NavBoxParser, ReferencesWrapParser).
    """

    def __init__(self) -> None:
        WikiElementParserMixin.__init__(self)
        self.sub_sub_sub_section_parser = SubSubSubSectionParser()

    def parse(self, element: Tag, context: WikiParserContext | None = None) -> dict[str, Any]:
        """Parsuje zawartość podpodsekcji.

        Dzieli element na podpodpodsekcje, parsuje każdą z nich
        za pomocą SubSubSubSectionParser.

        Args:
            element: Kontener zawierający elementy podpodsekcji.

        Returns:
            Słownik z listą podpodpodsekcji.
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
            Słownik z listą podpodpodsekcji.
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
                    **self.sub_sub_sub_section_parser.parse_group(group_elements, context=child_ctx),
                }
            )
        return {"sub_sub_sub_sections": parsed_sections}
