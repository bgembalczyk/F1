from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SectionDomainConfig:
    canonical_sections: frozenset[str]
    heading_aliases: Mapping[str, frozenset[str]]
