from collections.abc import Mapping
from typing import Protocol
from typing import runtime_checkable

from infrastructure.http_client.interfaces.http_response_protocol import (
    HttpResponseProtocol,
)


@runtime_checkable
class SessionProtocol(Protocol):
    """Minimalny kontrakt sesji HTTP wymagany przez klientów."""

    headers: Mapping[str, str]

    def get(
        self,
        url: str,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
    ) -> HttpResponseProtocol:
        """Wykonuje żądanie GET i zwraca odpowiedź zgodną z protokołem."""
        ...
