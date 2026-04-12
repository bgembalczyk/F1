from abc import ABC
from abc import abstractmethod
from typing import Generic

from bs4 import Tag

from scrapers.parsers.constants_contracts import TagOut
from scrapers.parsers.parser_abc import ParserABC


class TagParserABC(ParserABC[Tag, TagOut], ABC, Generic[TagOut]):
    """Canonical parser contract for single bs4.Tag inputs."""

    @abstractmethod
    def parse(self, raw: Tag) -> TagOut: ...
