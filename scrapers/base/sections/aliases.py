from __future__ import annotations

from scrapers.base.sections.constants import COMMON_SECTION_ALIASES
from scrapers.base.sections.constants import DOMAIN_SECTION_ALIASES
from scrapers.wiki.parsers.section_profiles import normalize_section_profile_key
from scrapers.wiki.parsers.section_profiles import profile_aliases_for_target


def builtin_aliases_for_target(target: str, *, domain: str | None) -> set[str]:
    normalized_target = normalize_section_profile_key(target)
    aliases = set(COMMON_SECTION_ALIASES.get(normalized_target, set()))
    aliases.update(profile_aliases_for_target(target, domain=domain))
    return aliases
