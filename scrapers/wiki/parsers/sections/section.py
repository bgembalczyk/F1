from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.result_model import TOP_SECTION_NAME
from scrapers.wiki.parsers.result_model import build_meta
from scrapers.wiki.parsers.result_model import build_result_item
from scrapers.wiki.parsers.result_model import split_section_meta
from scrapers.wiki.parsers.result_model import to_legacy_section
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import WikiElementParserMixin
from scrapers.wiki.parsers.sections.sub_sub_sub_section import _split_into_parts

_HEADING_CLASS = "mw-heading3"
_CHILD_KEY = "items"
_LEGACY_CHILD_KEY = "sub_sections"


class SectionParser(WikiElementParserMixin, WikiParser):
    def __init__(self) -> None:
        WikiElementParserMixin.__init__(self)
        self.sub_section_parser = SubSectionParser()

    def parse(self, element: Tag) -> dict[str, Any]:
        return self.parse_group(list(element.children))

    def parse_group(
        self,
        elements: list,
        *,
        parent_heading_path: list[str] | None = None,
    ) -> dict[str, Any]:
        tags = [c for c in elements if isinstance(c, Tag)]
        parts = _split_into_parts(tags, _HEADING_CLASS)
        parent_path = parent_heading_path or [TOP_SECTION_NAME]

        items = []
        for position, (name, group_elements) in enumerate(parts):
            section_id, heading_id, heading_path = split_section_meta(name, parent_path)
            parsed = self.sub_section_parser.parse_group(
                group_elements,
                parent_heading_path=heading_path,
            )
            item = build_result_item(
                "section",
                {_CHILD_KEY: parsed[_CHILD_KEY]},
                build_meta(
                    section_id=section_id,
                    heading_id=heading_id,
                    heading_path=heading_path,
                    position=position,
                ),
            )
            items.append(item)

        return {
            "items": items,
            _LEGACY_CHILD_KEY: [
                {
                    **to_legacy_section(item, _CHILD_KEY),
                    "sub_sub_sections": [
                        to_legacy_section(child, _CHILD_KEY) | {
                            "sub_sub_sub_sections": [
                                to_legacy_section(grand, _CHILD_KEY) | {
                                    "elements": [
                                        {"type": el["type"], "data": el["data"]}
                                        for el in grand["data"][_CHILD_KEY]
                                    ]
                                }
                                for grand in child["data"][_CHILD_KEY]
                            ]
                        }
                        for child in item["data"][_CHILD_KEY]
                    ],
                }
                for item in items
            ],
        }
