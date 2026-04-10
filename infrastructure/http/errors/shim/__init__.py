from infrastructure.http.errors.shim.base import HttpShimError
from infrastructure.http.errors.shim.http import HTTPError
from infrastructure.http.errors.shim.response_adapter import (
    HttpShimErrorResponseAdapter,
)
from infrastructure.http.errors.shim.timeout import HTTPTimeoutError

__all__ = [
    "HttpShimErrorResponseAdapter",
    "HttpShimError",
    "HTTPError",
    "HTTPTimeoutError",
]
