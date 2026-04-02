from __future__ import annotations

import re
from dataclasses import dataclass

from scrapers.wiki.sources_registry import FORMER_CONSTRUCTORS_SOURCE
from scrapers.wiki.sources_registry import INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE


@dataclass(frozen=True)
class SourceMetadata:
    domain: str
    source_name: str


@dataclass(frozen=True)
class ClassificationRule:
    tag: str
    domain: str | None = None
    source_name: str | None = None
    source_pattern: re.Pattern[str] | None = None

    def matches(self, metadata: SourceMetadata) -> bool:
        if self.domain is not None and self.domain != metadata.domain:
            return False
        if self.source_name is not None and self.source_name != metadata.source_name:
            return False
        if (
            self.source_pattern is not None
            and self.source_pattern.fullmatch(metadata.source_name) is None
        ):
            return False
        return True


CLASSIFICATION_RULES: tuple[ClassificationRule, ...] = (
    ClassificationRule(
        tag="constructor_indianapolis_only",
        domain="constructors",
        source_name=INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE,
    ),
    ClassificationRule(
        tag="constructor_former",
        domain="constructors",
        source_name=FORMER_CONSTRUCTORS_SOURCE,
    ),
    ClassificationRule(
        tag="engine_indianapolis_only",
        domain="engines",
        source_name="f1_indianapolis_only_engine_manufacturers.json",
    ),
    ClassificationRule(
        tag="engine_manufacturers",
        domain="engines",
        source_name="f1_engine_manufacturers.json",
    ),
    ClassificationRule(
        tag="team_constructor_snapshot",
        domain="teams",
        source_pattern=re.compile(r"f1_constructors_\d{4}\.json"),
    ),
    ClassificationRule(
        tag="team_sponsorship_liveries",
        domain="teams",
        source_name="f1_sponsorship_liveries.json",
    ),
    ClassificationRule(
        tag="team_privateer",
        domain="teams",
        source_name="f1_privateer_teams.json",
    ),
    ClassificationRule(
        tag="driver_f1",
        domain="drivers",
        source_name="f1_drivers.json",
    ),
    ClassificationRule(
        tag="driver_female",
        domain="drivers",
        source_name="female_drivers.json",
    ),
    ClassificationRule(
        tag="driver_fatalities",
        domain="drivers",
        source_name="f1_driver_fatalities.json",
    ),
    ClassificationRule(
        tag="race_red_flag_world_championship",
        domain="races",
        source_name="f1_red_flagged_world_championship_races.json",
    ),
    ClassificationRule(
        tag="race_red_flag_non_championship",
        domain="races",
        source_name="f1_red_flagged_non_championship_races.json",
    ),
)


@dataclass(frozen=True)
class SourceClassification:
    metadata: SourceMetadata
    tags: frozenset[str]

    def has(self, tag: str) -> bool:
        return tag in self.tags

    def describe_path(self) -> str:
        if not self.tags:
            return "default"
        return ",".join(sorted(self.tags))


def classify_source(metadata: SourceMetadata) -> SourceClassification:
    tags = frozenset(rule.tag for rule in CLASSIFICATION_RULES if rule.matches(metadata))
    return SourceClassification(metadata=metadata, tags=tags)
