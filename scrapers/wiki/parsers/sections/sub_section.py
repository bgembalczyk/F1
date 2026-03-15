from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.sections.sub_sub_section import SubSubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import WikiElementParserMixin
from scrapers.wiki.parsers.sections.sub_sub_sub_section import _split_into_parts

_HEADING_CLASS = "mw-heading4"


class SubSectionParser(WikiElementParserMixin, WikiParser):
    """Parser podsekcji Wikipedii (poziom 3).

    Przetwarza fragment HTML między kolejnymi:
    <div class="mw-heading mw-heading3"><h3 id=...>

    Dzieli zawartość na podpodsekcje (poziom 4) i deleguje ich parsowanie
    do SubSubSectionParser. Dodatkowo korzysta z narzędzi elementarnych
    (InfoboxParser, ParagrafParser, FigureParser, ListParser, TableParser,
    NavBoxParser, ReferencesWrapParser).
    """

    def __init__(self) -> None:
        WikiElementParserMixin.__init__(self)
        self.sub_sub_section_parser = SubSubSectionParser()

    def parse(self, element: Tag) -> dict[str, Any]:
        """Parsuje zawartość podsekcji.

        Dzieli element na podpodsekcje, parsuje każdą z nich
        za pomocą SubSubSectionParser.

        Args:
            element: Kontener zawierający elementy podsekcji.

        Returns:
            Słownik z listą podpodsekcji.
        """
        return self.parse_group(list(element.children))

    def parse_group(self, elements: list) -> dict[str, Any]:
        """Parsuje grupę elementów HTML.

        Args:
            elements: Lista elementów (potomków kontenera sekcji).

        Returns:
            Słownik z listą podpodsekcji.
        """
        tags = [c for c in elements if isinstance(c, Tag)]
        parts = _split_into_parts(tags, _HEADING_CLASS)
        return {
            "sub_sub_sections": [
                {
                    "name": name,
                    **self.sub_sub_section_parser.parse_group(group_elements),
                }
                for name, group_elements in parts
            ],
        }
