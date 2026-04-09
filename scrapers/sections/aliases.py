from __future__ import annotations

from scrapers.base.sections.constants import COMMON_SECTION_ALIASES
from scrapers.wiki.parsers.sections.helpers import DOMAIN_SECTION_PROFILES
from scrapers.wiki.parsers.sections.helpers import profile_aliases_for_target
from scrapers.wiki.parsers.sections.normalization import normalize_section_text


def _build_domain_section_aliases() -> dict[str, dict[str, set[str]]]:
    domain_aliases: dict[str, dict[str, set[str]]] = {}
    for domain, profile in DOMAIN_SECTION_PROFILES.items():
        domain_aliases[domain] = {
            normalize_section_text(target): set(aliases)
            for target, aliases in profile.heading_aliases.items()
        }
    return domain_aliases


DOMAIN_SECTION_ALIASES = _build_domain_section_aliases()


def builtin_aliases_for_target(target: str, *, domain: str | None) -> set[str]:
    normalized_target = normalize_section_text(target)
    aliases = set(COMMON_SECTION_ALIASES.get(normalized_target, set()))
    aliases.update(profile_aliases_for_target(target, domain=domain))
    return aliases
