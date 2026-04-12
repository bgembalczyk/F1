from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

from bs4 import Tag

from scrapers.parsers.tag_parser_abc import TagParserABC

Output = TypeVar("Output")


class InfoboxFieldParser(TagParserABC[Output], ABC, Generic[Output]):
    """Kontrakt runtime dla parserów pojedynczych pól infoboxu."""

    @abstractmethod
    def parse(self, raw: Tag) -> Output: ...


__all__ = ["InfoboxFieldParser", "Output"]
