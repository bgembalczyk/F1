from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class SectionDomainConfig:
    canonical_sections: frozenset[str]
    heading_aliases: Mapping[str, frozenset[str]]
