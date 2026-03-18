from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import TYPE_CHECKING
from typing import Any

from scrapers.wiki.parsers.sections.data_classes import SectionTree
from scrapers.wiki.parsers.sections.data_classes import SectionTreeMatch
from scrapers.wiki.parsers.sections.detection import normalize_section_text
from scrapers.wiki.parsers.sections.helpers import get_section_profile

if TYPE_CHECKING:
    from collections.abc import Iterable








def _normalize_id(text: str) -> str:
    return normalize_section_text(text).replace(" ", "_")


def _expand_targets(
    target: str,
    aliases: Iterable[str],
    *,
    domain: str | None = None,
) -> tuple[set[str], set[str]]:
    profile = get_section_profile(domain)
    if profile:
        canonical = profile.canonical_for(target)
        if canonical:
            target = canonical

    values = {target, *aliases}
    if profile:
        values.update(profile.aliases_for(target))
    normalized_texts = {
        normalize_section_text(value)
        for value in values
        if isinstance(value, str) and value.strip()
    }
    normalized_ids = {
        variant
        for text in normalized_texts
        for variant in (_normalize_id(text), text.replace(" ", "_"), text)
    }
    return normalized_ids, normalized_texts


def _iter_sections(sections: list[SectionTree]) -> Iterable[SectionTree]:
    for section in sections:
        yield section
        for key in ("sub_sections", "sub_sub_sections", "sub_sub_sub_sections"):
            children = section.get(key) or []
            if isinstance(children, list):
                yield from _iter_sections(children)


def _extract_sections(article: SectionTree | None) -> list[SectionTree]:
    if not isinstance(article, dict):
        return []

    if "sections" in article and isinstance(article["sections"], list):
        return article["sections"]

    content = article.get("content_text")
    if isinstance(content, dict) and isinstance(content.get("sections"), list):
        return content["sections"]

    return []


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


def _best_fuzzy_ratio(section_text: str, target_texts: set[str]) -> float:
    return max(
        SequenceMatcher(None, section_text, value).ratio() for value in target_texts
    )


def _find_match(
    sections: list[SectionTree],
    target: str,
    aliases: Iterable[str],
    *,
    domain: str | None = None,
    min_fuzzy_score: float,
) -> SectionTreeMatch | None:
    profile = get_section_profile(domain)
    if profile:
        canonical = profile.canonical_for(target)
        if canonical:
            target = canonical
        min_fuzzy_score = profile.priorities.fuzzy_threshold

    target_ids, target_texts = _expand_targets(target, aliases, domain=domain)
    fuzzy_candidates: list[SectionTreeMatch] = []

    for section in _iter_sections(sections):
        section_name = str(section.get("name", ""))
        section_id = str(section.get("section_id") or _normalize_id(section_name))
        if section_id in target_ids:
            return SectionTreeMatch(
                section=section,
                strategy="exact_id",
                score=_profile_score(profile, exact_id=True),
            )

        section_text = normalize_section_text(section_name)
        if section_text in target_texts:
            return SectionTreeMatch(
                section=section,
                strategy="exact_text",
                score=_profile_score(profile, exact_text=True),
            )

        if not target_texts:
            continue

        ratio = _best_fuzzy_ratio(section_text, target_texts)
        if ratio >= min_fuzzy_score:
            fuzzy_candidates.append(
                SectionTreeMatch(
                    section=section,
                    strategy="fuzzy",
                    score=_profile_score(profile) + ratio,
                ),
            )

    if not fuzzy_candidates:
        return None
    return max(fuzzy_candidates, key=lambda match: match.score)


def find_section_tree(
    article: SectionTree,
    target: str,
    aliases: Iterable[str] | None = None,
    *,
    domain: str | None = None,
    min_fuzzy_score: float = 0.82,
) -> SectionTree | None:
    """Find section fragment in ContentTextParser output.

    Supports matching by exact id-like name, aliases and fuzzy text score.
    Returns section subtree with nested sections/elements unchanged.
    """
    sections = _extract_sections(article)
    if not sections:
        return None

    match = _find_match(
        sections,
        target,
        aliases or set(),
        domain=domain,
        min_fuzzy_score=min_fuzzy_score,
    )
    if not match:
        return None
    return match.section


def collect_section_elements(
    section: SectionTree,
    element_type: str,
) -> list[dict[str, Any]]:
    """Collect parsed elements of a given type from section subtree."""

    found: list[dict[str, Any]] = [
        item
        for node in _iter_sections([section])
        for item in node.get("elements", [])
        if item.get("kind") == element_type or item.get("type") == element_type
    ]

    return found
