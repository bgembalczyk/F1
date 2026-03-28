from dataclasses import replace
from typing import TYPE_CHECKING

from infrastructure.http_client.caching.wiki import WikipediaCachePolicy
from infrastructure.http_client.policies.defaults import DEFAULT_HTTP_RETRIES
from infrastructure.http_client.policies.defaults import DEFAULT_HTTP_TIMEOUT
from infrastructure.http_client.policies.http import HttpPolicy
from infrastructure.http_client.policies.response_cache import ResponseCache

if TYPE_CHECKING:
    from scrapers.base.options import ScraperOptions


def default_http_policy() -> HttpPolicy:
    return HttpPolicy(
        cache=WikipediaCachePolicy.with_file_cache(),
        retries=DEFAULT_HTTP_RETRIES,
        timeout=DEFAULT_HTTP_TIMEOUT,
    )


def build_http_policy(
    *,
    timeout: int = DEFAULT_HTTP_TIMEOUT,
    retries: int = DEFAULT_HTTP_RETRIES,
    cache: ResponseCache | None = None,
) -> HttpPolicy:
    return HttpPolicy(
        timeout=timeout,
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
    from scrapers.base.options import ScraperOptions

    resolved = options or ScraperOptions()
    if include_urls is not None:
        resolved.include_urls = include_urls
    return resolved
