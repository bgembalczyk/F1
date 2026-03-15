from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from difflib import SequenceMatcher

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.text import clean_wiki_text

_HEADING_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6")

COMMON_SECTION_ALIASES: dict[str, set[str]] = {
    "results": {"result", "results and standings", "grands prix"},
    "career results": {
        "racing record",
        "career record",
        "motorsport career results",
        "racing career",
    },
}


@dataclass(slots=True)
class SectionMatch:
    heading: Tag
    strategy: str
    score: float


def normalize_section_text(text: str) -> str:
    return clean_wiki_text(text.replace("_", " ")).lower().strip()


def _normalize_id(text: str) -> str:
    return normalize_section_text(text).replace(" ", "_")


def _headline_text(heading: Tag) -> str:
    span = heading.find("span", class_="mw-headline")
    if isinstance(span, Tag):
        return span.get_text(" ", strip=True)
    return heading.get_text(" ", strip=True)


def _collect_heading_ids(heading: Tag) -> set[str]:
    ids: set[str] = set()
    heading_id = heading.get("id")
    if isinstance(heading_id, str) and heading_id.strip():
        ids.add(heading_id.strip())

    span = heading.find("span", class_="mw-headline")
    if isinstance(span, Tag):
        span_id = span.get("id")
        if isinstance(span_id, str) and span_id.strip():
            ids.add(span_id.strip())

    return ids


def _expand_target_values(target: str, aliases: set[str]) -> tuple[set[str], set[str]]:
    values = {target, *aliases}
    normalized_texts = {normalize_section_text(value) for value in values if value.strip()}
    normalized_ids = {
        variant
        for text in normalized_texts
        for variant in (_normalize_id(text), text.replace(" ", "_"), text)
    }
    return normalized_ids, normalized_texts


def _resolve_aliases(
    target: str,
    *,
    aliases: Mapping[str, set[str]] | None,
    domain_aliases: Mapping[str, Mapping[str, set[str]]] | None,
    domain: str | None,
) -> set[str]:
    normalized_target = normalize_section_text(target)
    resolved = set(COMMON_SECTION_ALIASES.get(normalized_target, set()))

    if domain and domain_aliases:
        per_domain = domain_aliases.get(domain, {})
        resolved.update(per_domain.get(normalized_target, set()))

    if aliases:
        resolved.update(aliases.get(normalized_target, set()))

    return resolved


def find_section_heading(
    soup: BeautifulSoup,
    target: str,
    *,
    aliases: Mapping[str, set[str]] | None = None,
    domain_aliases: Mapping[str, Mapping[str, set[str]]] | None = None,
    domain: str | None = None,
    min_fuzzy_score: float = 0.82,
) -> SectionMatch | None:
    resolved_aliases = _resolve_aliases(
        target,
        aliases=aliases,
        domain_aliases=domain_aliases,
        domain=domain,
    )
    target_ids, target_texts = _expand_target_values(target, resolved_aliases)

    fuzzy_candidates: list[SectionMatch] = []

    for heading in soup.find_all(_HEADING_TAGS):
        heading_ids = {_normalize_id(value) for value in _collect_heading_ids(heading)}
        if heading_ids & target_ids:
            return SectionMatch(heading=heading, strategy="exact_id", score=3.0)

        heading_text = normalize_section_text(_headline_text(heading))
        if heading_text in target_texts:
            return SectionMatch(heading=heading, strategy="exact_text", score=2.0)

        ratio = max(
            SequenceMatcher(None, heading_text, value).ratio()
            for value in target_texts
        )
        if ratio >= min_fuzzy_score:
            fuzzy_candidates.append(
                SectionMatch(heading=heading, strategy="fuzzy", score=1.0 + ratio),
            )

    if not fuzzy_candidates:
        return None

    return max(fuzzy_candidates, key=lambda match: match.score)
