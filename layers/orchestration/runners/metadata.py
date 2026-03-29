from __future__ import annotations

from typing import Literal
from typing import TypedDict


class RunnerMetadata(TypedDict):
    domain: str
    seed_name: str
    layer: Literal["layer_one"]
    output_category: str
    component_type: Literal["runner"]


def build_runner_metadata(
    domain: str,
    seed_name: str | None = None,
    output_category: str | None = None,
) -> RunnerMetadata:
    normalized_seed_name = seed_name or domain
    normalized_output_category = output_category or domain
    return {
        "domain": domain,
        "seed_name": normalized_seed_name,
        "layer": "layer_one",
        "output_category": normalized_output_category,
        "component_type": "runner",
    }
