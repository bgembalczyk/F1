from collections.abc import Mapping
from typing import Protocol
from typing import runtime_checkable

from infrastructure.http.protocols.response import HttpResponseProtocol
from infrastructure.http.protocols.session import SessionProtocol
from infrastructure.http.type_alias import JsonValue


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

    def get_batch(
        self,
        urls: list[str],
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
        max_workers: int = 10,
    ) -> list[HttpResponseProtocol]:
        """Wykonuje GET dla wielu URLi współbieżnie."""
        ...

    def get_text_batch(
        self,
        urls: list[str],
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
        max_workers: int = 10,
    ) -> list[str]:
        """Zwraca tekst (str) wielu odpowiedzi współbieżnie po wywołaniu GET."""
        ...

    def get_json_batch(
        self,
        urls: list[str],
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
        max_workers: int = 10,
    ) -> list[JsonValue]:
        """Zwraca JSON parsując odpowiedzi współbieżnie jako JSON."""
        ...


__all__ = [
    "HttpClientProtocol",
]
