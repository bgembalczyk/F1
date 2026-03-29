from __future__ import annotations

from dataclasses import dataclass

from scrapers.wiki.component_metadata import ComponentMetadata
from scrapers.wiki.component_metadata import RUNNER_KIND
from scrapers.wiki.component_metadata import build_component_metadata


@dataclass(frozen=True)
class RunnerMetadata:
    domain: str
    seed_name: str
    output_category: str

    def to_component_metadata(self) -> ComponentMetadata:
        return build_component_metadata(
            domain=self.domain,
            kind=RUNNER_KIND,
            seed_name=self.seed_name,
            output_category=self.output_category,
        )


def build_runner_metadata(
    *,
    domain: str,
    seed_name: str | None = None,
    output_category: str | None = None,
) -> ComponentMetadata:
    normalized_seed_name = seed_name or domain
    normalized_output_category = output_category or domain
    return RunnerMetadata(
        domain=domain,
        seed_name=normalized_seed_name,
        output_category=normalized_output_category,
    ).to_component_metadata()
