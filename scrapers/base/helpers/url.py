"""URL normalization helpers shared across scrapers."""

from urllib.parse import urljoin
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

from models.domain_utils.season_urls import FORMULA_ONE_SEASON_URL_TEMPLATE
from models.domain_utils.season_urls import FORMULA_ONE_SEASONS_LIST_URL
from models.domain_utils.season_urls import WIKIPEDIA_BASE_URL
from models.domain_utils.season_urls import WIKIPEDIA_WIKI_PATH
from models.validation.utils import is_valid_url

__all__ = [
    "FORMULA_ONE_SEASONS_LIST_URL",
    "FORMULA_ONE_SEASON_URL_TEMPLATE",
    "WIKIPEDIA_BASE_URL",
    "WIKIPEDIA_WIKI_PATH",
    "normalize_url",
]


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
