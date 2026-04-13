"""Facade module for wiki section parsing utilities.

Re-exports the canonical section-parsing API so consumers can import from
``scrapers.parsers.wiki.sections`` without depending on internal layout.
"""

from scrapers.parsers.section.adapt import find_section_tree
from scrapers.parsers.section.detection import find_section_heading
from scrapers.parsers.section.domain_config.dataclass import SectionDomainConfig
from scrapers.parsers.section.domain_config.helpers import (
    validate_section_profiles_config,
)
from scrapers.parsers.section.helpers import DOMAIN_SECTION_PROFILES
from scrapers.parsers.section.helpers import profile_entry_aliases

__all__ = [
    "DOMAIN_SECTION_PROFILES",
    "SectionDomainConfig",
    "find_section_heading",
    "find_section_tree",
    "profile_entry_aliases",
    "validate_section_profiles_config",
]
