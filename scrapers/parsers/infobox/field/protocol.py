from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

from bs4 import Tag

from scrapers.parsers.contracts.infobox_field_parser_abc import InfoboxFieldParserABC

Output = TypeVar("Output")


class InfoboxFieldParser(InfoboxFieldParserABC[Output], ABC, Generic[Output]):
    """Silny kontrakt runtime dla parserów pojedynczych pól infoboxu."""

    @abstractmethod
    def parse(self, raw: Tag) -> Output: ...


__all__ = ["InfoboxFieldParser", "Output"]
