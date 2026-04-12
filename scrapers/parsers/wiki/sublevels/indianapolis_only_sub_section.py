from typing import Any

from bs4 import Tag

from scrapers.parsers.list_element.indianapolis_constructors import (
    IndianapolisConstructorsListParser,
)
from scrapers.parsers.wiki.sublevels.sub_section import SubSectionParser


class GenericIndianapolisOnlySubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._list_parser = IndianapolisConstructorsListParser()

    def parse(self, element: Tag, *args: Any, **kwargs: Any) -> dict[str, Any]:
        list_root = element.find(["ul", "ol"])
        if isinstance(list_root, Tag):
            return self._list_parser.parse(list_root)
        return self._parse_group(list(element.children), *args, **kwargs)

    def _parse_group(
        self,
        elements: list,
        *_args: Any,
        **_kwargs: Any,
    ) -> dict[str, Any]:
        for candidate in elements:
            if isinstance(candidate, Tag) and candidate.name in {"ul", "ol"}:
                return self._list_parser.parse(candidate)
        return {"items": []}


__all__ = ["GenericIndianapolisOnlySubSectionParser"]
