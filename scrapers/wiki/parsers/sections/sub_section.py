from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.result_model import TOP_SECTION_NAME
from scrapers.wiki.parsers.result_model import build_meta
from scrapers.wiki.parsers.result_model import build_result_item
from scrapers.wiki.parsers.result_model import split_section_meta
from scrapers.wiki.parsers.result_model import to_legacy_section
from scrapers.wiki.parsers.sections.sub_sub_section import SubSubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import WikiElementParserMixin
from scrapers.wiki.parsers.sections.sub_sub_sub_section import _split_into_parts

_HEADING_CLASS = "mw-heading4"
_CHILD_KEY = "items"
_LEGACY_CHILD_KEY = "sub_sub_sections"


class SubSectionParser(WikiElementParserMixin, WikiParser):
    def __init__(self) -> None:
        WikiElementParserMixin.__init__(self)
        self.sub_sub_section_parser = SubSubSectionParser()

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
            parsed = self.sub_sub_section_parser.parse_group(
                group_elements,
                parent_heading_path=heading_path,
            )
            item = build_result_item(
                "sub_section",
                {
                    _CHILD_KEY: parsed[_CHILD_KEY],
                },
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
                    "sub_sub_sub_sections": [
                        to_legacy_section(child, _CHILD_KEY) | {"elements": [
                            {"type": e["type"], "data": e["data"]}
                            for e in child["data"][_CHILD_KEY]
                        ]}
                        for child in item["data"][_CHILD_KEY]
                    ],
                }
                for item in items
            ],
        }
