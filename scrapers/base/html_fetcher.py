from infrastructure.http_client.interfaces.http_client_protocol import (
    HttpClientProtocol,
)
from scrapers.base.source_adapter import SourceAdapter
from scrapers.base.options import HttpPolicy


class HtmlFetcher(SourceAdapter):
    """Warstwa pobierania HTML z opcjonalnym cache."""

    def __init__(
        self,
        *,
        policy: HttpPolicy,
        http_client: HttpClientProtocol,
    ) -> None:
        self.policy = policy
        self.http_client = http_client
        self.timeout = policy.timeout
        self._metadata = {
            "policy": policy,
            "cache": policy.cache,
            "retries": policy.retries,
            "timeout": policy.timeout,
        }

    @property
    def metadata(self) -> dict[str, object]:
        return dict(self._metadata)

    def get_text(self, url: str, *, timeout: int | None = None) -> str:
        return self.http_client.get_text(url, timeout=timeout or self.timeout)

    def get(self, url: str) -> str:
        return self.get_text(url)
