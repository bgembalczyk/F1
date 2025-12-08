from __future__ import annotations

from typing import Dict, Mapping, Optional, Protocol, runtime_checkable


@runtime_checkable
class HttpResponseProtocol(Protocol):
    status_code: int
    headers: Mapping[str, str]
    text: str

    def raise_for_status(self) -> None:
        ...


@runtime_checkable
class HttpClientProtocol(Protocol):
    session: object

    def get(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> HttpResponseProtocol:
        ...

    def get_text(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> str:
        ...
