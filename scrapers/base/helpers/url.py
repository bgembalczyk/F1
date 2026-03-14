"""URL normalization helpers shared across scrapers."""

from urllib.parse import urljoin
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

from models.validation.utils import is_valid_url


def normalize_url(base: str, href: str | None) -> str | None:
    """
    Buduje i waliduje pełny URL na podstawie bazy i href.

    Obsługuje przypadki:
    - względne ścieżki (/wiki/...),
    - schemowe URL-e (//...),
    - absolutne URL-e (http/https).
    """
    href_normalized = (href or "").strip()
    if not href_normalized:
        return None

    parsed_href = urlsplit(href_normalized)
    if parsed_href.scheme:
        url = href_normalized
    elif href_normalized.startswith("//"):
        base_scheme = urlsplit(base).scheme or "https"
        url = f"{base_scheme}:{href_normalized}"
    elif href_normalized.startswith("/"):
        base_parts = urlsplit(base)
        scheme = base_parts.scheme or "https"
        if base_parts.netloc:
            url = urlunsplit((scheme, base_parts.netloc, href_normalized, "", ""))
        else:
            url = urljoin(base, href_normalized)
    else:
        url = urljoin(base, href_normalized)

    if not is_valid_url(url):
        return None

    parsed_url = urlsplit(url)
    if "//" in parsed_url.path:
        return None

    return url
