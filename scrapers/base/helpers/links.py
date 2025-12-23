"""Helper utilities for link normalization."""

from typing import Iterable

from models.records import LinkRecord
from models.validation.validators import normalize_link_record
from scrapers.base.helpers.text_normalization import clean_wiki_text, is_language_link
from scrapers.base.helpers.wiki import is_wikipedia_redlink, strip_marks


def _empty_link_record(*, drop_empty: bool) -> LinkRecord | None:
    if drop_empty:
        return None
    return {"text": "", "url": None}


def _normalize_single_link(
    link: LinkRecord | None,
    *,
    strip_marks_text: bool = True,
    drop_empty: bool = True,
    strip_lang_suffix: bool = True,
) -> LinkRecord | None:
    if not link:
        return _empty_link_record(drop_empty=drop_empty)

    text = link.get("text") or ""
    url = link.get("url")

    if strip_marks_text:
        text = strip_marks(text) or ""

    text = clean_wiki_text(text, strip_lang_suffix=strip_lang_suffix)

    if strip_lang_suffix and is_language_link(text, url):
        return _empty_link_record(drop_empty=drop_empty)

    if is_wikipedia_redlink(url):
        url = None

    normalized = normalize_link_record({"text": text, "url": url})
    if normalized is None:
        return _empty_link_record(drop_empty=drop_empty)
    return normalized


def normalize_links(
    links: Iterable[LinkRecord] | LinkRecord | None,
    *,
    strip_marks: bool = True,
    drop_empty: bool = True,
    strip_lang_suffix: bool = True,
) -> list[LinkRecord]:
    if isinstance(links, dict):
        links_iterable: Iterable[LinkRecord] = [links]
    else:
        links_iterable = links or []

    normalized_links: list[LinkRecord] = []
    for link in links_iterable:
        normalized = _normalize_single_link(
            link,
            strip_marks_text=strip_marks,
            drop_empty=drop_empty,
            strip_lang_suffix=strip_lang_suffix,
        )
        if normalized is None:
            continue
        normalized_links.append(normalized)

    return normalized_links
