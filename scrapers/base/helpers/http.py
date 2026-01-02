from infrastructure.http_client.caching.wiki import WikipediaCachePolicy
from infrastructure.http_client.policies.http import HttpPolicy
from infrastructure.http_client.policies.response_cache import ResponseCache
from scrapers.base.options import ScraperOptions


def default_http_policy() -> HttpPolicy:
    return HttpPolicy(cache=WikipediaCachePolicy.with_file_cache())


def build_http_policy(
    *,
    timeout: int = 10,
    retries: int = 0,
    cache: ResponseCache | None = None,
) -> HttpPolicy:
    return HttpPolicy(
        timeout=timeout,
        retries=retries,
        cache=cache,
    )


def init_scraper_options(
    options: ScraperOptions | None,
    *,
    include_urls: bool | None = None,
) -> ScraperOptions:
    resolved = options or ScraperOptions()
    if include_urls is not None:
        resolved.include_urls = include_urls
    return resolved
