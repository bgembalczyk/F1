"""DEPRECATED: use `scrapers.wiki.parsers.sections.section_profiles` instead."""

from __future__ import annotations

# Deprecated shim: import from dedicated module listed below.

from scrapers.wiki.parsers.sections.section_profiles import (
    DOMAIN_SECTION_PROFILES,
    get_section_profile,
    profile_aliases_for_target,
    profile_entry_aliases,
    _split_into_parts,
    _copy_common_aliases,
    _build_profile_aliases,
    _build_domain_profile,
    _build_profiles,
)


__all__ = [
    'DOMAIN_SECTION_PROFILES', 'get_section_profile', 'profile_aliases_for_target', 'profile_entry_aliases', '_split_into_parts', '_copy_common_aliases', '_build_profile_aliases', '_build_domain_profile', '_build_profiles',
]
