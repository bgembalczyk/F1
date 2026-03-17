from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from scrapers.base.helpers.text import clean_wiki_text
from scrapers.wiki.parsers.constants import BASE_COMMON_ALIASES
from scrapers.wiki.parsers.constants import CURRENT_CONSTRUCTORS_ID


def normalize_section_profile_key(value: str) -> str:
    return clean_wiki_text(value.replace("_", " ")).lower().strip()


@dataclass(frozen=True, slots=True)
class SectionMatchPriorities:
    exact_id_score: float = 3.0
    exact_text_score: float = 2.0
    fuzzy_base_score: float = 1.0
    fuzzy_threshold: float = 0.82


@dataclass(frozen=True, slots=True)
class SectionProfile:
    domain: str
    canonical_section_ids: frozenset[str]
    heading_aliases: dict[str, frozenset[str]]
    priorities: SectionMatchPriorities = field(
        default_factory=SectionMatchPriorities,
    )
    required_sections: frozenset[str] = frozenset()
    optional_sections: frozenset[str] = frozenset()

    def aliases_for(self, target: str) -> set[str]:
        normalized_target = normalize_section_profile_key(target)
        aliases = set(self.heading_aliases.get(normalized_target, frozenset()))
        if normalized_target in self.canonical_section_ids:
            aliases.update(self.heading_aliases.get(normalized_target, frozenset()))
        return aliases

    def canonical_for(self, target: str) -> str | None:
        normalized_target = normalize_section_profile_key(target)
        if normalized_target in self.canonical_section_ids:
            return normalized_target

        for canonical, aliases in self.heading_aliases.items():
            if normalized_target in aliases:
                return canonical
        return None


def _domain_aliases() -> dict[str, dict[str, set[str]]]:
    return {
        "seasons": {
            "results": {"grands prix", "results and standings"},
            "regulation changes": {"rule changes"},
            "mid-season changes": {"driver changes"},
        },
        "drivers": {
            "career results": {"racing record", "karting record"},
            "racing record": {"motorsport career results"},
            "non-championship": {"non-championship races"},
        },
        "circuits": {
            "circuits": {"formula one circuits", "list of formula one circuits"},
            "results": {"race results"},
            "layout history": {"history"},
            "events": {"races"},
            "lap records": {"formula one lap records"},
        },
        "constructors": {
            "former constructors": {"defunct constructors"},
            "championship results": {"formula one/world championship results"},
            "complete formula one results": {"complete world championship results"},
        },
        "grands_prix": {},
    }


def _canonical_sections() -> dict[str, set[str]]:
    return {
        "drivers": {"career results", "racing record", "non-championship"},
        "constructors": {
            "history",
            "championship results",
            "complete formula one results",
            "former constructors",
        },
        "circuits": {"circuits", "layout history", "lap records", "events", "results"},
        "seasons": {
            "results",
            "regulation changes",
            "mid-season changes",
            "calendar",
            "standings",
        },
        "grands_prix": {"by year", "winners"},
    }


def _build_profiles() -> dict[str, SectionProfile]:
    canonical = _canonical_sections()
    domain_aliases = _domain_aliases()
    profiles: dict[str, SectionProfile] = {}

    for domain, canonical_sections in canonical.items():
        aliases: dict[str, set[str]] = {
            key: set(values) for key, values in BASE_COMMON_ALIASES.items()
        }
        for key, values in domain_aliases.get(domain, {}).items():
            aliases.setdefault(key, set()).update(values)

        profiles[domain] = SectionProfile(
            domain=domain,
            canonical_section_ids=frozenset(canonical_sections),
            heading_aliases={key: frozenset(values) for key, values in aliases.items()},
            required_sections=frozenset(),
            optional_sections=frozenset(canonical_sections),
        )

    return profiles


DOMAIN_SECTION_PROFILES = _build_profiles()


def get_section_profile(domain: str | None) -> SectionProfile | None:
    if not domain:
        return None
    return DOMAIN_SECTION_PROFILES.get(domain)


def profile_aliases_for_target(target: str, *, domain: str | None) -> set[str]:
    profile = get_section_profile(domain)
    if not profile:
        return set()

    normalized_target = normalize_section_profile_key(target)
    aliases = set(profile.aliases_for(normalized_target))

    if domain == "constructors" and CURRENT_CONSTRUCTORS_ID.match(normalized_target):
        aliases.update(
            {
                "constructors for the current season",
                "current constructors",
                "constructors",
            },
        )

    return aliases


def profile_entry_aliases(
    domain: str,
    section_id: str,
    *fallback_aliases: str,
) -> tuple[str, ...]:
    profile = get_section_profile(domain)
    merged: list[str] = []
    seen: set[str] = set()

    def add(value: str) -> None:
        normalized = normalize_section_profile_key(value)
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        merged.append(value)

    for alias in fallback_aliases:
        add(alias)

    if profile:
        for alias in sorted(profile.aliases_for(section_id)):
            add(alias)

    return tuple(merged)
