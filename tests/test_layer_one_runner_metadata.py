from __future__ import annotations

import pytest

from layers.orchestration.helpers import build_layer_one_runner_map
from layers.orchestration.runners.metadata import build_runner_metadata
from scrapers.wiki.component_metadata import ComponentMetadata


@pytest.mark.unit
def test_build_runner_metadata_uses_domain_seed_and_output_category() -> None:
    metadata = build_runner_metadata(
        domain="drivers",
        seed_name="drivers_custom",
        output_category="teams",
    )

    assert metadata == ComponentMetadata(
        domain="drivers",
        seed_name="drivers_custom",
        layer="layer_one",
        output_category="teams",
        component_type="runner",
        default_output_path=None,
        legacy_output_path=None,
    )


@pytest.mark.unit
def test_all_layer_one_runners_expose_consistent_metadata_shape() -> None:
    runner_map = build_layer_one_runner_map()

    for seed_name, runner in runner_map.items():
        metadata = getattr(runner, "COMPONENT_METADATA")

        assert isinstance(metadata, ComponentMetadata)
        assert metadata.layer == "layer_one"
        assert metadata.component_type == "runner"
        assert metadata.seed_name == seed_name
        assert metadata.domain
        assert metadata.output_category
