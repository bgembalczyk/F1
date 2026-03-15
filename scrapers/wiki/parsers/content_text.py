from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.result_model import TOP_SECTION_NAME
from scrapers.wiki.parsers.result_model import build_meta
from scrapers.wiki.parsers.result_model import build_result_item
from scrapers.wiki.parsers.result_model import split_section_meta
from scrapers.wiki.parsers.result_model import to_legacy_section
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import _split_into_parts

_HEADING_CLASS = "mw-heading2"


class ContentTextParser(WikiParser):
    def __init__(self) -> None:
        self.section_parser = SectionParser()

    def parse(self, element: Tag) -> dict[str, Any]:
        tags = [c for c in element.children if isinstance(c, Tag)]
        parts = _split_into_parts(tags, _HEADING_CLASS)

        items = []
        for position, (name, group_elements) in enumerate(parts):
            section_id, heading_id, heading_path = split_section_meta(name, [])
            parsed = self.section_parser.parse_group(
                group_elements,
                parent_heading_path=heading_path,
            )
            items.append(
                build_result_item(
                    "article_section",
                    {"items": parsed["items"]},
                    build_meta(
                        section_id=section_id,
                        heading_id=heading_id,
                        heading_path=heading_path,
                        position=position,
                    ),
                ),
            )

        return {
            "items": items,
            "sections": [
                {
                    **to_legacy_section(item, "items"),
                    "sub_sections": [
                        to_legacy_section(child, "items") | {
                            "sub_sub_sections": [
                                to_legacy_section(grand, "items") | {
                                    "sub_sub_sub_sections": [
                                        to_legacy_section(great, "items") | {
                                            "elements": [
                                                {"type": el["type"], "data": el["data"]}
                                                for el in great["data"]["items"]
                                            ]
                                        }
                                        for great in grand["data"]["items"]
                                    ]
                                }
                                for grand in child["data"]["items"]
                            ]
                        }
                        for child in item["data"]["items"]
                    ],
                }
                for item in items
            ],
        }
