from collections.abc import Mapping
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class HttpResponseProtocol(Protocol):
    """Kontrakt minimalnej odpowiedzi HTTP wykorzystywanej przez klientów."""

    status_code: int
    headers: Mapping[str, str]
    text: str

    def raise_for_status(self) -> None: ...
