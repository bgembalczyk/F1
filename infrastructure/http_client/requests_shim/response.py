from dataclasses import dataclass
from collections.abc import Mapping

from infrastructure.http_client.requests_shim.constants import HTTP_BAD_REQUEST
from infrastructure.http_client.requests_shim.http_error import HTTPError


@dataclass(frozen=True)
class Response:
    url: str
    status_code: int
    headers: Mapping[str, str]
    text: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "headers", {str(k): str(v) for k, v in self.headers.items()})

    def raise_for_status(self) -> None:
        if self.status_code >= HTTP_BAD_REQUEST:
            raise HTTPError(self.url, self.status_code, self.text, self.headers)
