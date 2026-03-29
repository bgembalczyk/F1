from __future__ import annotations

from dataclasses import dataclass

from scrapers.wiki.component_metadata import ComponentMetadata
from scrapers.wiki.component_metadata import RUNNER_KIND


@dataclass(frozen=True)
class RunnerMetadata:
    domain: str
    seed_name: str
    layer: str
    output_category: str
    component_type: str

    @classmethod
    def from_component_metadata(cls, metadata: ComponentMetadata) -> "RunnerMetadata":
        return cls(
            domain=metadata.domain,
            seed_name=metadata.seed_name,
            layer=metadata.layer,
            output_category=metadata.output_category,
            component_type=metadata.component_type,
        )

    @classmethod
    def build(cls, *, domain: str, seed_name: str | None = None) -> "RunnerMetadata":
        normalized_seed_name = seed_name or domain
        return cls(
            domain=domain,
            seed_name=normalized_seed_name,
            layer="layer_one",
            output_category=domain,
            component_type=RUNNER_KIND,
        )
