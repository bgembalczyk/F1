from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Generic
from typing import Protocol
from typing import TypeVar

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.options import ScraperOptions

if TYPE_CHECKING:
    from collections.abc import Iterable

    from scrapers.base.parsers.soup import SoupParser

ParserInputT = TypeVar("ParserInputT")


@dataclass(frozen=True)
class InfoboxExtractionResult:
    """Wspólny kontrakt wyniku ekstrakcji infoboxów."""

    records: list[dict[str, Any]]

    @property
    def primary_record(self) -> dict[str, Any]:
        return self.records[0] if self.records else {}












