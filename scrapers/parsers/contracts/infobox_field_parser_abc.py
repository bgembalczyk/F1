from abc import ABC
from abc import abstractmethod
from typing import TypeVar

from bs4 import Tag

from scrapers.parsers.contracts import TagParserABC


FieldValue = TypeVar("FieldValue")

class InfoboxFieldParserABC(TagParserABC[FieldValue], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> FieldValue: ...

