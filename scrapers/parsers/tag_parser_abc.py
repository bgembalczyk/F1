from abc import ABC
from abc import abstractmethod
from typing import Generic

from bs4 import Tag

from scrapers.parsers.contracts.parser_abc import ParserABC
from scrapers.parsers.contracts.constants_contracts import TagOut


class TagParserABC(ParserABC[Tag, TagOut], ABC, Generic[TagOut]):
    """Canonical parser contract for single bs4.Tag inputs."""

    @abstractmethod
    def parse(self, raw: Tag) -> TagOut: ...
