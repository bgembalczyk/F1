from typing import Any

from models.records.circuit_base import CircuitBaseRecord


class CircuitDetailsRecord(CircuitBaseRecord):
    url: str
    infobox: dict[str, Any]
    tables: list[dict[str, Any]]
