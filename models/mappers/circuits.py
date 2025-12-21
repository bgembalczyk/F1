from __future__ import annotations

from typing import Any, Mapping

from models.circuit import Circuit


def from_scraped_circuit(data: Mapping[str, Any] | Circuit) -> Circuit:
    if isinstance(data, Circuit):
        return data
    return Circuit(**dict(data))
