from layers.orchestration.runner_registry import _build_explicit_layer_one_runner_map

EXPECTED_METADATA_KEYS = {
    "domain",
    "seed_name",
    "layer",
    "output_category",
    "component_type",
}


def test_explicit_layer_one_runners_expose_consistent_metadata_fields() -> None:
    runner_map = _build_explicit_layer_one_runner_map()

    for seed_name, runner in runner_map.items():
        metadata = runner.COMPONENT_METADATA
        assert set(metadata) == EXPECTED_METADATA_KEYS
        assert metadata["seed_name"] == seed_name
        assert metadata["layer"] == "layer_one"
        assert metadata["component_type"] == "runner"
