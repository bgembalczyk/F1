from __future__ import annotations

from scrapers.wiki.parsers.sections.helpers import DOMAIN_SECTION_PROFILES
from scrapers.wiki.parsers.sections.helpers import get_section_profile
from scrapers.wiki.parsers.sections.helpers import profile_aliases_for_target
from scrapers.wiki.parsers.sections.helpers import profile_entry_aliases
from scrapers.wiki.parsers.sections.normalization import normalize_section_profile_key

__all__ = [
    "DOMAIN_SECTION_PROFILES",
    "get_section_profile",
    "normalize_section_profile_key",
    "profile_aliases_for_target",
    "profile_entry_aliases",
]
