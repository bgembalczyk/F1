from collections.abc import Mapping
from typing import Protocol
from typing import TypeAlias
from typing import runtime_checkable

from infrastructure.http_client.interfaces import HttpResponseProtocol
from infrastructure.http_client.interfaces import SessionProtocol

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


@runtime_checkable
class HttpClientProtocol(Protocol):
    """Kontrakt klienta HTTP zgodnego z biblioteką requests."""

    session: SessionProtocol

    def get(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
    ) -> HttpResponseProtocol:
        """Wykonuje GET i zwraca obiekt odpowiedzi; wyjątek dla błędów HTTP."""
        ...

    def get_text(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
    ) -> str:
        """Zwraca tekst (str) odpowiedzi po wywołaniu GET."""
        ...

    def get_json(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
    ) -> JsonValue:
        """Zwraca JSON (dict/list/etc.) parsując treść odpowiedzi jako JSON."""
        ...


__all__ = [
    "HttpClientProtocol",
    "JsonValue",
    "JsonScalar",
]
