from typing import Any
from typing import TypedDict


class CircuitDetailsRecord(TypedDict):
    url: str
    infobox: dict[str, Any]
    tables: list[dict[str, Any]]
