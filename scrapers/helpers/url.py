"""URL normalization helpers shared across scrapers."""

URL_HELPERS_DEPRECATION_NOTE = (
    "DEPRECATED: prefer UrlResolverStrategyRegistry (migration iteration: 2026-Q2). "
    "Planned removal after one migration iteration."
)


def resolve_url(
    base: str,
    href: str | None,
    *,
    domain: str | None = None,
) -> str | None:
    """Resolve URL via central UrlResolverStrategyRegistry."""
    from scrapers.url_resolver import DEFAULT_URL_RESOLVER_STRATEGY_REGISTRY

    return DEFAULT_URL_RESOLVER_STRATEGY_REGISTRY.resolve_url(
        base_url=base,
        href=href,
        domain=domain,
    )


def normalize_url(
    base: str,
    href: str | None,
    *,
    domain: str | None = None,
) -> str | None:
    """Deprecated URL helper kept for one migration iteration."""
    return resolve_url(base, href, domain=domain)


__all__ = ["URL_HELPERS_DEPRECATION_NOTE", "normalize_url", "resolve_url"]
