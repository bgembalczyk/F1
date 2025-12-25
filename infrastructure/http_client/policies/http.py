from dataclasses import dataclass

from infrastructure.http_client.policies.response_cache import ResponseCache


@dataclass(frozen=True)
class HttpPolicy:
    cache: ResponseCache | None = None
    retries: int = 0
    timeout: int = 10

    def __post_init__(self) -> None:
        if self.timeout <= 0:
            raise ValueError("timeout must be greater than 0")
        if self.retries < 0:
            raise ValueError("retries must be >= 0")
