from __future__ import annotations

from scrapers.wiki.parsers.section_profiles import DOMAIN_SECTION_PROFILES
from scrapers.wiki.parsers.section_profiles import normalize_section_profile_key
from scrapers.wiki.parsers.section_profiles import profile_aliases_for_target

COMMON_SECTION_ALIASES: dict[str, set[str]] = {
    "results": {"result", "results and standings", "grands prix"},
    "career results": {
        "racing record",
        "career record",
        "motorsport career results",
        "racing career",
    },
}

DOMAIN_SECTION_ALIASES: dict[str, dict[str, set[str]]] = {
    domain: {key: set(values) for key, values in profile.heading_aliases.items()}
    for domain, profile in DOMAIN_SECTION_PROFILES.items()
}


def builtin_aliases_for_target(target: str, *, domain: str | None) -> set[str]:
    normalized_target = normalize_section_profile_key(target)
    aliases = set(COMMON_SECTION_ALIASES.get(normalized_target, set()))
    aliases.update(profile_aliases_for_target(target, domain=domain))
    return aliases
