from collections.abc import Mapping
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class HttpErrorProtocol(Protocol):
    """Minimalny kontrakt błędu wymagany przez klient HTTP."""

    url: str
    status: int
    reason: str
    headers: Mapping[str, str]

