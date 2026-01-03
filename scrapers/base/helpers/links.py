"""Helper utilities for link normalization."""

from typing import Callable, Iterable

from bs4 import BeautifulSoup, Tag

from models.records.link import LinkRecord
from models.validation.validators import normalize_and_validate_link_dict
from scrapers.base.helpers.text import clean_wiki_text, strip_marks
from scrapers.base.helpers.text_normalization import is_language_link
from scrapers.base.helpers.wiki import is_reference_link, is_wikipedia_redlink


def empty_link_record(*, drop_empty: bool) -> LinkRecord | None:
    if drop_empty:
        return None
    return {"text": "", "url": None}


def normalize_single_link(
    link: LinkRecord | None,
    *,
    strip_marks_text: bool = True,
    drop_empty: bool = True,
    strip_lang_suffix: bool = True,
) -> LinkRecord | None:
    if not link:
        return empty_link_record(drop_empty=drop_empty)

    text = link.get("text") or ""
    url = link.get("url")

    if strip_marks_text:
        text = strip_marks(text) or ""

    text = clean_wiki_text(text, strip_lang_suffix=strip_lang_suffix)

    if strip_lang_suffix and is_language_link(text, url):
        return empty_link_record(drop_empty=drop_empty)

    if is_wikipedia_redlink(url):
        url = None

    normalized = normalize_and_validate_link_dict(
        {"text": text, "url": url}, field_name="link"
    )
    if normalized is None:
        return empty_link_record(drop_empty=drop_empty)
    return normalized


def normalize_links(
    links: Iterable[LinkRecord] | LinkRecord | Tag | str | None,
    *,
    full_url: Callable[[str], str] | None = None,
    allow_local_anchors: bool = True,
    strip_marks: bool = True,
    drop_empty: bool = True,
    strip_lang_suffix: bool = True,
) -> list[LinkRecord]:
    if isinstance(links, Tag) or isinstance(links, str):
        if isinstance(links, Tag):
            search_root = links
        else:
            search_root = BeautifulSoup(links or "", "html.parser")
        links_iterable = []
        for anchor in search_root.find_all("a", href=True):
            if is_reference_link(anchor, allow_local_anchors=allow_local_anchors):
                continue
            href = str(anchor.get("href") or "")
            url = full_url(href) if full_url else href
            links_iterable.append(
                {"text": anchor.get_text(strip=True), "url": url}
            )
    elif isinstance(links, dict):
        links_iterable: Iterable[LinkRecord] = [links]
    else:
        links_iterable = links or []

    normalized_links: list[LinkRecord] = []
    for link in links_iterable:
        normalized = normalize_single_link(
            link,
            strip_marks_text=strip_marks,
            drop_empty=drop_empty,
            strip_lang_suffix=strip_lang_suffix,
        )
        if normalized is None:
            continue
        normalized_links.append(normalized)

    return normalized_links
