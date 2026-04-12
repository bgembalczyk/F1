from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic

from scrapers.parsers.constants_contracts import RecordT_co
from scrapers.parsers.constants_contracts import TableInputT_contra


class ParseGroupMixin(ABC, Generic[TableInputT_contra, RecordT_co]):
    """Shared mixin for payloads that can produce grouped parsed records."""

    @abstractmethod
    def parse_group(self, table: TableInputT_contra) -> list[RecordT_co]: ...


class GroupParsingMixin(ParseGroupMixin[TableInputT_contra, RecordT_co], ABC):
    """Named mixin for parse_group capability."""


__all__ = ["ParseGroupMixin", "GroupParsingMixin"]
