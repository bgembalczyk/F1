"""Polityka klasyfikacji kodów statusów HTTP."""

from infrastructure.http_client.policies.constants import SERVER_ERROR_END
from infrastructure.http_client.policies.constants import SERVER_ERROR_START
from infrastructure.http_client.policies.constants import TOO_MANY_REQUESTS
from infrastructure.http_client.requests_shim.constants import HTTP_BAD_REQUEST


class HttpStatusPolicy:
    """Klasyfikuje statusy HTTP dla obsługi błędów i retry."""

    @staticmethod
    def is_error(status_code: int) -> bool:
        return int(status_code) >= HTTP_BAD_REQUEST

    @staticmethod
    def is_retryable(status_code: int) -> bool:
        normalized_status = int(status_code)
        return normalized_status == TOO_MANY_REQUESTS or (
            SERVER_ERROR_START <= normalized_status <= SERVER_ERROR_END
        )
