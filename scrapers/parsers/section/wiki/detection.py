from __future__ import annotations

import re
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from bs4 import Tag

from models.domain_utils.field_normalization.aliases import expand_alias_variants
from scrapers.helpers.constants import HEADING_TAGS
from scrapers.parsers.section.match.dataclass import SectionMatch
from scrapers.parsers.section.wiki.helpers import best_fuzzy_ratio
from scrapers.parsers.section.wiki.helpers import get_section_profile
from scrapers.parsers.section.wiki.normalization import normalize_section_text
from scrapers.section.aliases import builtin_aliases_for_target

if TYPE_CHECKING:
    from collections.abc import Mapping


def normalize_section_slug(text: str) -> str:
    """Create stable section slug used in parser output IDs.

    Keeps wikipedia-like underscores while removing unstable punctuation.
    """
    normalized = normalize_section_text(text)
    sanitized = re.sub(r"[^a-z0-9\s_-]", "", normalized)
    collapsed = re.sub(r"[\s_-]+", "_", sanitized).strip("_")
    return collapsed or "section"


def normalize_section_lookup_key(value: str) -> str:
    """Normalize separators so '-', '_' and spaces compare equally."""
    normalized = normalize_section_text(value)
    return re.sub(r"[\s_-]+", " ", normalized).strip()


def make_stable_section_id(
    *,
    heading_anchor: str | None,
    heading_text: str,
    breadcrumbs: tuple[str, ...] = (),
) -> str:
    """Build stable section identifier from heading anchor + normalized slug."""
    anchor_slug = normalize_section_slug(heading_anchor) if heading_anchor else ""
    text_slug = normalize_section_slug(heading_text)
    breadcrumb_slug = "__".join(
        normalize_section_slug(item) for item in breadcrumbs if item
    )
    if anchor_slug:
        return anchor_slug
    if breadcrumb_slug:
        return f"{breadcrumb_slug}__{text_slug}"
    return text_slug


def headline_text(heading: Tag) -> str:
    span = heading.find("span", class_="mw-headline")
    if isinstance(span, Tag):
        return span.get_text(" ", strip=True)
    return heading.get_text(" ", strip=True)


def collect_heading_ids(heading: Tag) -> set[str]:
    ids: set[str] = set()
    heading_id = heading.get("id")
    if isinstance(heading_id, str) and heading_id.strip():
        ids.add(heading_id.strip())

    for span in heading.find_all("span"):
        if not isinstance(span, Tag):
            continue
        span_id = span.get("id")
        if isinstance(span_id, str) and span_id.strip():
            ids.add(span_id.strip())

    return ids


def expand_target_values(target: str, aliases: set[str]) -> tuple[set[str], set[str]]:
    values = {target, *aliases}
    return expand_alias_variants(values, text_normalizer=normalize_section_text)


def resolve_aliases(
    target: str,
    *,
    aliases: Mapping[str, set[str]] | None,
    domain_aliases: Mapping[str, Mapping[str, set[str]]] | None,
    domain: str | None,
) -> set[str]:
    normalized_target = normalize_section_lookup_key(target)
    resolved = builtin_aliases_for_target(target, domain=domain)

    if domain and domain_aliases:
        resolved.update(domain_aliases.get(domain, {}).get(normalized_target, set()))

    if aliases:
        resolved.update(aliases.get(normalized_target, set()))
        resolved.update(aliases.get(target, set()))

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
    profile = get_section_profile(domain)
    if profile:
        canonical = profile.canonical_for(target)
        if canonical:
            target = canonical
        min_fuzzy_score = profile.priorities.fuzzy_threshold

    resolved_aliases = resolve_aliases(
        target,
        aliases=aliases,
        domain_aliases=domain_aliases,
        domain=domain,
    )
    _, target_texts = expand_target_values(target, resolved_aliases)
    target_lookup_keys = {
        normalize_section_lookup_key(value)
        for value in {target, *resolved_aliases}
        if isinstance(value, str) and value.strip()
    }

    fuzzy_candidates: list[SectionMatch] = []

    for heading in soup.find_all(HEADING_TAGS):
        heading_ids = {
            normalize_section_lookup_key(value)
            for value in collect_heading_ids(heading)
        }
        if heading_ids & target_lookup_keys:
            return SectionMatch(
                heading=heading,
                strategy="exact_id",
                score=profile.priorities.get_score(exact_id=True) if profile else 3.0,
            )

        heading_text = normalize_section_text(headline_text(heading))
        if normalize_section_lookup_key(heading_text) in target_lookup_keys:
            return SectionMatch(
                heading=heading,
                strategy="exact_text",
                score=profile.priorities.get_score(exact_text=True) if profile else 2.0,
            )

        ratio = best_fuzzy_ratio(heading_text, target_texts)
        if ratio >= min_fuzzy_score:
            base_score = profile.priorities.get_score() if profile else 1.0
            fuzzy_candidates.append(
                SectionMatch(
                    heading=heading,
                    strategy="fuzzy",
                    score=base_score + ratio,
                ),
            )

    if not fuzzy_candidates:
        return None

    return max(fuzzy_candidates, key=lambda match: match.score)


__all__ = [
    "normalize_section_slug",
    "normalize_section_lookup_key",
    "make_stable_section_id",
    "headline_text",
    "collect_heading_ids",
    "expand_target_values",
    "resolve_aliases",
    "find_section_heading",
]
