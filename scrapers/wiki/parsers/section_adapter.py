from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any

from scrapers.wiki.parsers.section_detection import COMMON_SECTION_ALIASES
from scrapers.wiki.parsers.section_detection import normalize_section_text

SectionTree = dict[str, Any]


@dataclass(slots=True)
class SectionTreeMatch:
    section: SectionTree
    strategy: str
    score: float


def _normalize_id(text: str) -> str:
    return normalize_section_text(text).replace(" ", "_")


def _expand_targets(target: str, aliases: Iterable[str]) -> tuple[set[str], set[str]]:
    normalized_target = normalize_section_text(target)
    values = {target, *aliases, *COMMON_SECTION_ALIASES.get(normalized_target, set())}
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
    min_fuzzy_score: float,
) -> SectionTreeMatch | None:
    target_ids, target_texts = _expand_targets(target, aliases)
    fuzzy_candidates: list[SectionTreeMatch] = []

    for section in _iter_sections(sections):
        section_name = str(section.get("name", ""))
        section_id = _normalize_id(section_name)
        if section_id in target_ids:
            return SectionTreeMatch(section=section, strategy="exact_id", score=3.0)

        section_text = normalize_section_text(section_name)
        if section_text in target_texts:
            return SectionTreeMatch(section=section, strategy="exact_text", score=2.0)

        if not target_texts:
            continue

        ratio = max(
            SequenceMatcher(None, section_text, value).ratio() for value in target_texts
        )
        if ratio >= min_fuzzy_score:
            fuzzy_candidates.append(
                SectionTreeMatch(section=section, strategy="fuzzy", score=1.0 + ratio)
            )

    if not fuzzy_candidates:
        return None
    return max(fuzzy_candidates, key=lambda match: match.score)


def find_section_tree(
    article: SectionTree,
    target: str,
    aliases: Iterable[str] | None = None,
    *,
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
            if item.get("type") == element_type:
                found.append(item)
        for key in ("sub_sections", "sub_sub_sections", "sub_sub_sub_sections"):
            for child in node.get(key, []):
                if isinstance(child, dict):
                    walk(child)

    walk(section)
    return found
