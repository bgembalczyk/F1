from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any

from scrapers.wiki.parsers.section_detection import normalize_section_text
from scrapers.wiki.parsers.section_profiles import get_section_profile

SectionTree = dict[str, Any]


@dataclass(slots=True)
class SectionExtractionContext:
    """Shared context passed through every section parser layer."""

    page_title: str = ""
    page_url: str = ""
    breadcrumbs: tuple[str, ...] = ()
    html_metadata: dict[str, Any] | None = None
    section_id: str | None = None

    def with_section(self, *, section_name: str, section_id: str | None = None) -> "SectionExtractionContext":
        return SectionExtractionContext(
            page_title=self.page_title,
            page_url=self.page_url,
            breadcrumbs=(*self.breadcrumbs, section_name),
            html_metadata=self.html_metadata,
            section_id=section_id,
        )


@dataclass(slots=True)
class SectionTreeMatch:
    section: SectionTree
    strategy: str
    score: float


def _normalize_id(text: str) -> str:
    return normalize_section_text(text).replace(" ", "_")


def _expand_targets(target: str, aliases: Iterable[str], *, domain: str | None = None) -> tuple[set[str], set[str]]:
    profile = get_section_profile(domain)
    if profile:
        canonical = profile.canonical_for(target)
        if canonical:
            target = canonical

    values = {target, *aliases}
    if profile:
        values.update(profile.aliases_for(target))
    normalized_texts = {
        normalize_section_text(value) for value in values if isinstance(value, str) and value.strip()
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
            exact_id_score = profile.priorities.exact_id_score if profile else 3.0
            return SectionTreeMatch(section=section, strategy="exact_id", score=exact_id_score)

        section_text = normalize_section_text(section_name)
        if section_text in target_texts:
            exact_text_score = profile.priorities.exact_text_score if profile else 2.0
            return SectionTreeMatch(section=section, strategy="exact_text", score=exact_text_score)

        if not target_texts:
            continue

        ratio = max(
            SequenceMatcher(None, section_text, value).ratio() for value in target_texts
        )
        if ratio >= min_fuzzy_score:
            fuzzy_base_score = profile.priorities.fuzzy_base_score if profile else 1.0
            fuzzy_candidates.append(
                SectionTreeMatch(section=section, strategy="fuzzy", score=fuzzy_base_score + ratio)
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


def collect_section_elements(section: SectionTree, element_type: str) -> list[dict[str, Any]]:
    """Collect parsed elements of a given type from section subtree."""

    found: list[dict[str, Any]] = []

    def walk(node: SectionTree) -> None:
        for item in node.get("elements", []):
            if item.get("kind") == element_type or item.get("type") == element_type:
                found.append(item)
        for key in ("sub_sections", "sub_sub_sections", "sub_sub_sub_sections"):
            for child in node.get(key, []):
                if isinstance(child, dict):
                    walk(child)

    walk(section)
    return found
