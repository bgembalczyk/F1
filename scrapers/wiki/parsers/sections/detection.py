from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.transform_micro_ops import expand_alias_variants
from scrapers.base.sections.aliases import builtin_aliases_for_target
from scrapers.wiki.parsers.constants import HEADING_TAGS
from scrapers.wiki.parsers.sections.data_classes import SectionMatch
from scrapers.wiki.parsers.sections.helpers import get_section_profile
from scrapers.wiki.parsers.sections.normalization import normalize_section_text

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

    for span in heading.find_all("span"):
        if not isinstance(span, Tag):
            continue
        span_id = span.get("id")
        if isinstance(span_id, str) and span_id.strip():
            ids.add(span_id.strip())

    return ids


def _expand_target_values(target: str, aliases: set[str]) -> tuple[set[str], set[str]]:
    values = {target, *aliases}
    return expand_alias_variants(values, text_normalizer=normalize_section_text)


def _resolve_aliases(
    target: str,
    *,
    aliases: Mapping[str, set[str]] | None,
    domain_aliases: Mapping[str, Mapping[str, set[str]]] | None,
    domain: str | None,
) -> set[str]:
    normalized_target = normalize_section_text(target)
    resolved = builtin_aliases_for_target(target, domain=domain)

    if domain and domain_aliases:
        resolved.update(domain_aliases.get(domain, {}).get(normalized_target, set()))

    if aliases:
        resolved.update(aliases.get(normalized_target, set()))

    return resolved


def _profile_score(
    profile: object | None,
    *,
    exact_id: bool = False,
    exact_text: bool = False,
) -> float:
    if profile is None:
        if exact_id:
            return 3.0
        if exact_text:
            return 2.0
        return 1.0
    if exact_id:
        return profile.priorities.exact_id_score
    if exact_text:
        return profile.priorities.exact_text_score
    return profile.priorities.fuzzy_base_score


def _best_fuzzy_ratio(heading_text: str, target_texts: set[str]) -> float:
    return max(
        SequenceMatcher(None, heading_text, value).ratio() for value in target_texts
    )


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

    resolved_aliases = _resolve_aliases(
        target,
        aliases=aliases,
        domain_aliases=domain_aliases,
        domain=domain,
    )
    target_ids, target_texts = _expand_target_values(target, resolved_aliases)

    fuzzy_candidates: list[SectionMatch] = []

    for heading in soup.find_all(HEADING_TAGS):
        heading_ids = {
            normalize_section_text(value).replace(" ", "_")
            for value in _collect_heading_ids(heading)
        }
        if heading_ids & target_ids:
            return SectionMatch(
                heading=heading,
                strategy="exact_id",
                score=_profile_score(profile, exact_id=True),
            )

        heading_text = normalize_section_text(_headline_text(heading))
        if heading_text in target_texts:
            return SectionMatch(
                heading=heading,
                strategy="exact_text",
                score=_profile_score(profile, exact_text=True),
            )

        ratio = _best_fuzzy_ratio(heading_text, target_texts)
        if ratio >= min_fuzzy_score:
            fuzzy_candidates.append(
                SectionMatch(
                    heading=heading,
                    strategy="fuzzy",
                    score=_profile_score(profile) + ratio,
                ),
            )

    if not fuzzy_candidates:
        return None

    return max(fuzzy_candidates, key=lambda match: match.score)
