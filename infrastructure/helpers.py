from dataclasses import replace
from typing import TYPE_CHECKING

from config.app.provider import AppConfigProvider
from infrastructure.cache.wiki_policy import WikipediaCachePolicy
from infrastructure.http.policies.constants import DEFAULT_HTTP_RETRIES
from infrastructure.http.policies.http import HttpPolicy
from infrastructure.http.protocols.text_cache import TextCacheProtocol

if TYPE_CHECKING:
    from scrapers.base.options import ScraperOptions


def default_http_policy() -> HttpPolicy:
    # di-antipattern-allow: config provider access is intentionally deferred to runtime.
    timeout = AppConfigProvider().get_http_config().timeout_seconds
    return HttpPolicy(
        cache=WikipediaCachePolicy.with_file_cache(),
        retries=DEFAULT_HTTP_RETRIES,
        timeout=timeout,
    )


def build_http_policy(
    *,
    timeout: int | None = None,
    retries: int = DEFAULT_HTTP_RETRIES,
    cache: TextCacheProtocol | None = None,
) -> HttpPolicy:
    resolved_timeout = (
        timeout
        if timeout is not None
        else AppConfigProvider().get_http_config().timeout_seconds
    )
    return HttpPolicy(
        timeout=resolved_timeout,
        retries=retries,
        cache=cache,
    )


def init_scraper_options(
    options: "ScraperOptions | None",
    *,
    include_urls: bool | None = None,
) -> "ScraperOptions":
    """Zwróć nową instancję ``ScraperOptions`` bez mutowania argumentu wejściowego.

    Semantyka helpera jest immutable:
    - zawsze zwracana jest nowa instancja opcji (copy/replace),
    - `include_urls` może nadpisać wyłącznie pole `ScraperOptions.include_urls`,
    - pozostałe pola są kopiowane 1:1 z wejściowych opcji.
    """
    # di-antipattern-allow: local import by design.
    from scrapers.base.options import ScraperOptions

    base_options = options or ScraperOptions()
    if include_urls is None:
        return replace(base_options)
    return replace(base_options, include_urls=include_urls)
