from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

NodeInputT = TypeVar("NodeInputT")
NodeOutputT = TypeVar("NodeOutputT")


class WikiNodeParserABC(ABC, Generic[NodeInputT, NodeOutputT]):
    """Base contract for parsers handling a single wiki HTML node category."""

    @abstractmethod
    def parse(self, raw: NodeInputT) -> NodeOutputT: ...


__all__ = ["WikiNodeParserABC"]
