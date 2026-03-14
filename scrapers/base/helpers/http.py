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
    if policy is not None:
        options.policy = policy
    return options.to_http_policy()


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
