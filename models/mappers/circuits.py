from collections.abc import Mapping
from typing import Any

from models.validation.circuit import Circuit


def from_scraped_circuit(data: Mapping[str, Any] | Circuit) -> Circuit:
    if isinstance(data, Circuit):
        return data
    return Circuit(**dict(data))
