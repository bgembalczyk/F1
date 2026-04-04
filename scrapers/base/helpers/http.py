from dataclasses import replace
from typing import TYPE_CHECKING

from config.app_config_provider import AppConfigProvider
from infrastructure.http_client.caching.wiki import WikipediaCachePolicy
from infrastructure.http_client.policies.constants import DEFAULT_HTTP_RETRIES
from infrastructure.http_client.policies.http import HttpPolicy
from infrastructure.http_client.policies.response_cache import ResponseCache

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
    cache: ResponseCache | None = None,
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


def resolve_http_policy(
    options: "ScraperOptions",
    *,
    policy: HttpPolicy | None = None,
) -> HttpPolicy:
    base_policy = policy or options.http.policy
    timeout = options.http.timeout
    retries = options.http.retries
    if timeout is None and retries is None:
        return base_policy
    return replace(
        base_policy,
        timeout=timeout if timeout is not None else base_policy.timeout,
        retries=retries if retries is not None else base_policy.retries,
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
    # di-antipattern-allow: local import prevents runtime circular dependencies.
    from scrapers.base.options import ScraperOptions

    base_options = options or ScraperOptions()
    if include_urls is None:
        return replace(base_options)
    return replace(base_options, include_urls=include_urls)
