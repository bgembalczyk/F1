from __future__ import annotations

import logging
from collections import Counter
from collections.abc import Mapping

from scrapers.base.helpers.text import clean_wiki_text

logger = logging.getLogger(__name__)


AliasRegistry = dict[str, dict[str, tuple[str, ...]]]


def _normalize(value: str) -> str:
    return clean_wiki_text(value.replace("_", " ")).lower().strip()


SECTION_ALIAS_REGISTRY: AliasRegistry = {
    "common": {
        "results": ("result", "results and standings", "grands prix"),
        "career results": (
            "racing record",
            "career record",
            "motorsport career results",
            "racing career",
        ),
    },
    "drivers": {
        "career results": ("racing record", "karting record"),
    },
    "seasons": {
        "results": ("grands prix", "results and standings"),
        "scoring system": ("points scoring system",),
        "non-championship races": ("non-championship race",),
    },
    "grands_prix": {
        "by year": (
            "winners",
            "by year: the european grand prix as a standalone event",
            "winners of the caesars palace grand prix",
        ),
        "red-flagged races": (
            "world championship races",
            "championship races",
            "red flagged races",
            "world_championship_races",
        ),
        "non-championship races": (
            "non-championship",
            "non championship races",
        ),
    },
    "circuits": {
        "results": ("race results",),
    },
}

_ALIAS_HITS: Counter[tuple[str, str, str, str]] = Counter()


def get_aliases(domain: str | None, canonical_section: str) -> list[str]:
    normalized_canonical = _normalize(canonical_section)
    aliases = list(SECTION_ALIAS_REGISTRY.get("common", {}).get(normalized_canonical, ()))
    if domain:
        aliases.extend(
            SECTION_ALIAS_REGISTRY.get(domain, {}).get(normalized_canonical, ()),
        )
    # preserve order while de-duplicating
    return list(dict.fromkeys(aliases))


def get_section_candidates(domain: str | None, canonical_section: str) -> list[str]:
    return [canonical_section, *get_aliases(domain, canonical_section)]


def register_alias_hit(
    *,
    domain: str,
    canonical_section: str,
    alias: str,
    strategy: str,
) -> None:
    canonical = _normalize(canonical_section)
    alias_key = _normalize(alias)
    key = (domain, canonical, alias_key, strategy)
    _ALIAS_HITS[key] += 1
    logger.info(
        "Section alias hit domain=%s canonical=%s alias=%s strategy=%s count=%d",
        domain,
        canonical,
        alias_key,
        strategy,
        _ALIAS_HITS[key],
    )


def get_alias_telemetry() -> Mapping[tuple[str, str, str, str], int]:
    return dict(_ALIAS_HITS)


def reset_alias_telemetry() -> None:
    _ALIAS_HITS.clear()
