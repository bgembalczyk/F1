from __future__ import annotations

import re
from dataclasses import dataclass

from scrapers.wiki.constants import CHASSIS_CONSTRUCTOR_DOMAINS
from scrapers.wiki.constants import FORMER_CONSTRUCTORS_SOURCE
from scrapers.wiki.constants import INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE
from scrapers.wiki.constants import TYRE_MANUFACTURERS_SOURCE


@dataclass(frozen=True)
class RecordRoutingDecision:
    domain: str
    source_type: str
    transform_chain: tuple[str, ...]
    postprocess_chain: tuple[str, ...]


@dataclass(frozen=True)
class RecordClassifierInput:
    domain: str
    source_name: str


class RecordClassifier:
    _transform_chain_by_domain: dict[str, tuple[str, ...]] = {
        "constructors": ("constructor_domain",),
        "constructor": ("constructor_domain",),
        "chassis": ("constructor_domain",),
        "circuits": ("circuits_domain",),
        "engines": ("engines_domain",),
        "grands_prix": ("grands_prix_domain",),
        "teams": ("teams_domain",),
        "drivers": ("drivers_domain",),
        "races": ("races_domain",),
    }

    _postprocess_chain_by_domain: dict[str, tuple[str, ...]] = {
        "drivers": ("merge_duplicate_drivers", "sort_drivers_by_name"),
        "constructors": ("sort_constructors_by_name",),
        "constructor": ("sort_constructors_by_name",),
        "chassis": ("sort_constructors_by_name",),
        "teams": (
            "merge_duplicate_teams",
            "nest_team_liveries",
            "sort_teams_by_name",
        ),
        "seasons": ("sort_seasons_by_year",),
    }

    def classify(self, metadata: RecordClassifierInput) -> RecordRoutingDecision:
        source_type = self._source_type(metadata.domain, metadata.source_name)
        transform_chain = self._resolve_transform_chain(metadata.domain, metadata.source_name)
        postprocess_chain = self._postprocess_chain_by_domain.get(metadata.domain, ())
        return RecordRoutingDecision(
            domain=metadata.domain,
            source_type=source_type,
            transform_chain=transform_chain,
            postprocess_chain=postprocess_chain,
        )

    def _resolve_transform_chain(self, domain: str, source_name: str) -> tuple[str, ...]:
        chain: list[str] = []
        if source_name == TYRE_MANUFACTURERS_SOURCE:
            chain.append("tyre_manufacturers")
        chain.extend(self._transform_chain_by_domain.get(domain, ()))
        return tuple(chain)

    def _source_type(self, domain: str, source_name: str) -> str:
        if source_name == TYRE_MANUFACTURERS_SOURCE:
            return "tyre_manufacturers"
        if source_name == INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE:
            return "indianapolis_only"
        if source_name == FORMER_CONSTRUCTORS_SOURCE:
            return "former_constructor"
        if domain == "constructors" and re.fullmatch(r"f1_constructors_\d{4}\.json", source_name):
            return "yearly_constructors"
        if domain == "races" and "world_championship" in source_name:
            return "world_championship_races"
        if domain == "races" and "non_championship" in source_name:
            return "non_championship_races"
        if domain in CHASSIS_CONSTRUCTOR_DOMAINS:
            return "constructor_domain"
        if domain:
            return f"{domain}_default"
        return "unknown"
