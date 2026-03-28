from dataclasses import dataclass

from infrastructure.http_client.policies.constants import DEFAULT_HTTP_BACKOFF_SECONDS
from infrastructure.http_client.policies.constants import DEFAULT_HTTP_RETRIES
from infrastructure.http_client.policies.constants import DEFAULT_HTTP_TIMEOUT


@dataclass(frozen=True)
class HttpPolicyDefaults:
    timeout: int = DEFAULT_HTTP_TIMEOUT
    retries: int = DEFAULT_HTTP_RETRIES
    backoff_seconds: float = DEFAULT_HTTP_BACKOFF_SECONDS
