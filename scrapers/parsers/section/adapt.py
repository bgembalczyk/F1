from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from models.domain_utils.field_normalization.aliases import expand_alias_variants
from scrapers.parsers.section.match.tree import SectionTree
from scrapers.parsers.section.match.tree import SectionTreeMatch
from scrapers.parsers.section.wiki.helpers import best_fuzzy_ratio
from scrapers.parsers.section.wiki.helpers import get_section_profile
from scrapers.parsers.section.wiki.normalization import normalize_section_text

if TYPE_CHECKING:
    from collections.abc import Iterable


def expand_targets(
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
    return expand_alias_variants(values, text_normalizer=normalize_section_text)


def iter_sections(sections: list[SectionTree]) -> Iterable[SectionTree]:
    for section in sections:
        yield section
        for key in ("sub_sections", "sub_sub_sections", "sub_sub_sub_sections"):
            children = section.get(key) or []
            if isinstance(children, list):
                yield from iter_sections(children)


def extract_sections(article: SectionTree | None) -> list[SectionTree]:
    if not isinstance(article, dict):
        return []

    if "sections" in article and isinstance(article["sections"], list):
        return article["sections"]

    content = article.get("content_text")
    if isinstance(content, dict) and isinstance(content.get("sections"), list):
        return content["sections"]

    return []


def find_match(
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
        min_fuzzy_score = getattr(
            profile.priorities,
            "fuzzy_threshold",
            min_fuzzy_score,
        )

    target_ids, target_texts = expand_targets(target, aliases, domain=domain)
    fuzzy_candidates: list[SectionTreeMatch] = []

    for section in iter_sections(sections):
        section_name = str(section.get("name", ""))
        section_id = str(
            section.get("section_id")
            or normalize_section_text(section_name).replace(" ", "_"),
        )
        if section_id in target_ids:
            return SectionTreeMatch(
                section=section,
                strategy="exact_id",
                score=profile.priorities.get_score(exact_id=True) if profile else 3.0,
            )

        section_text = normalize_section_text(section_name)
        if section_text in target_texts:
            return SectionTreeMatch(
                section=section,
                strategy="exact_text",
                score=profile.priorities.get_score(exact_text=True) if profile else 2.0,
            )

        if not target_texts:
            continue

        ratio = best_fuzzy_ratio(section_text, target_texts)
        if ratio >= min_fuzzy_score:
            base_score = profile.priorities.get_score() if profile else 1.0
            fuzzy_candidates.append(
                SectionTreeMatch(
                    section=section,
                    strategy="fuzzy",
                    score=base_score + ratio,
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
    sections = extract_sections(article)
    if not sections:
        return None

    match = find_match(
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
        for node in iter_sections([section])
        for item in node.get("elements", [])
        if item.get("kind") == element_type or item.get("type") == element_type
    ]

    return found


__all__ = [
    "expand_targets",
    "iter_sections",
    "extract_sections",
    "find_match",
    "find_section_tree",
    "collect_section_elements",
]
