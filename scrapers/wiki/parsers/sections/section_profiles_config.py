from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from scrapers.wiki.parsers.sections.normalization import normalize_section_profile_key
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


@dataclass(frozen=True, slots=True)
class SectionDomainConfig:
    canonical_sections: frozenset[str]
    heading_aliases: Mapping[str, frozenset[str]]


SECTION_PROFILES_CONFIG: Mapping[str, SectionDomainConfig] = {
    "seasons": SectionDomainConfig(
        canonical_sections=frozenset(
            {
                "regulation changes",
                "mid-season changes",
            },
        ),
        heading_aliases={
            "regulation changes": frozenset({"rule changes"}),
            "mid-season changes": frozenset({"driver changes"}),
        },
    ),
    "drivers": SectionDomainConfig(
        canonical_sections=frozenset(
            {"career results", "racing record", "non-championship"},
        ),
        heading_aliases={
            "career results": frozenset({"racing record", "karting record"}),
            "racing record": frozenset({"motorsport career results"}),
            "non-championship": frozenset({"non-championship races"}),
        },
    ),
    "circuits": SectionDomainConfig(
        canonical_sections=frozenset({"layout history", "lap records", "events"}),
        heading_aliases={
            "layout history": frozenset({"history"}),
            "events": frozenset({"races"}),
            "lap records": frozenset({"formula one lap records"}),
        },
    ),
    "constructors": SectionDomainConfig(
        canonical_sections=frozenset(
            {
                "history",
                "championship results",
                "complete formula one results",
            },
        ),
        heading_aliases={
            "championship results": frozenset(
                {"formula one/world championship results"},
            ),
            "complete formula one results": frozenset(
                {"complete world championship results"},
            ),
        },
    ),
    "grands_prix": SectionDomainConfig(
        canonical_sections=frozenset({"by year", "winners"}),
        heading_aliases={},
    ),
}


def validate_section_profiles_config(
    config: Mapping[str, SectionDomainConfig],
) -> None:
    for domain, domain_config in config.items():
        normalized_canonical = {
            normalize_section_profile_key(value)
            for value in domain_config.canonical_sections
        }

        invalid_canonical_keys = [
            canonical
            for canonical in domain_config.heading_aliases
            if normalize_section_profile_key(canonical) not in normalized_canonical
        ]
        if invalid_canonical_keys:
            raise ValueError(
                "Invalid canonical ids in heading_aliases for "
                f"domain={domain}: {sorted(invalid_canonical_keys)}",
            )

        alias_to_canonical: dict[str, set[str]] = defaultdict(set)
        for canonical, aliases in domain_config.heading_aliases.items():
            normalized_canonical_id = normalize_section_profile_key(canonical)
            for alias in aliases:
                normalized_alias = normalize_section_profile_key(alias)
                if normalized_alias:
                    alias_to_canonical[normalized_alias].add(normalized_canonical_id)

        duplicated_aliases = {
            alias: sorted(canonicals)
            for alias, canonicals in alias_to_canonical.items()
            if len(canonicals) > 1
        }
        if duplicated_aliases:
            raise ValueError(
                "Duplicated aliases in section profile config for "
                f"domain={domain}: {duplicated_aliases}",
            )
