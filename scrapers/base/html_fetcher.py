from __future__ import annotations

from infrastructure.http_client.interfaces import HttpClientProtocol

from scrapers.base.source_adapter import SourceAdapter
from scrapers.base.options import HttpPolicy


class HtmlFetcher(SourceAdapter[str]):
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

    def get_text(self, url: str, *, timeout: int | None = None) -> str:
        return self.http_client.get_text(url, timeout=timeout or self.timeout)

    def get(self, source: str | None = None, **kwargs: object) -> str:
        if source is None:
            raise ValueError("HtmlFetcher wymaga URL-a jako źródła.")
        timeout = kwargs.get("timeout")
        return self.get_text(
            source, timeout=timeout if isinstance(timeout, int) else None
        )
