from __future__ import annotations

from typing import Any
from typing import Protocol
from typing import runtime_checkable

from bs4 import BeautifulSoup


@runtime_checkable
class InfoboxParserProtocol(Protocol):
    def parse(self, fragment: BeautifulSoup) -> dict[str, Any]: ...


__all__ = ["InfoboxParserProtocol"]
