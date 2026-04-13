from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic

from scrapers.parsers.constants_contracts import In
from scrapers.parsers.constants_contracts import Out


class ParserABC(ABC, Generic[In, Out]):
    """Canonical parser contract (input -> output)."""

    @abstractmethod
    def parse(self, raw: In) -> Out: ...
