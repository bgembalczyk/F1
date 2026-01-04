from dataclasses import dataclass

DEFAULT_HTTP_TIMEOUT = 10
DEFAULT_HTTP_RETRIES = 0
DEFAULT_HTTP_BACKOFF_SECONDS = 0.5


@dataclass(frozen=True)
class HttpPolicyDefaults:
    timeout: int = DEFAULT_HTTP_TIMEOUT
    retries: int = DEFAULT_HTTP_RETRIES
    backoff_seconds: float = DEFAULT_HTTP_BACKOFF_SECONDS
