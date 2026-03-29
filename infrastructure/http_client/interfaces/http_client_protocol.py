from typing import Any
from typing import Protocol
from typing import runtime_checkable

from infrastructure.http_client.interfaces.http_response_protocol import (
    HttpResponseProtocol,
)
from infrastructure.http_client.interfaces.session_protocol import SessionProtocol


@runtime_checkable
class HttpClientProtocol(Protocol):
    """Kontrakt klienta HTTP zgodnego z biblioteką requests."""

    session: SessionProtocol

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> HttpResponseProtocol:
        """Wykonuje GET i zwraca obiekt odpowiedzi; wyjątek dla błędów HTTP."""
        ...

    def get_text(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> str:
        """Zwraca tekst (str) odpowiedzi po wywołaniu GET."""
        ...

    def get_json(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> Any:
        """Zwraca JSON (dict/list/etc.) parsując treść odpowiedzi jako JSON."""
        ...
