from typing import Any
from typing import Protocol
from typing import TypeAlias


ScraperRecord: TypeAlias = dict[str, Any]
ScraperRecords: TypeAlias = list[ScraperRecord]


class ListScraperProtocol(Protocol):
    def fetch(self) -> ScraperRecords: ...


class SingleScraperProtocol(Protocol):
    def fetch_by_url(self, url: str) -> ScraperRecords: ...
