from pathlib import Path

from layers.facade import WikiPipelineFacade

EXPECTED_SCENARIO_RUNS = 2


class _LayerExecutorSpy:
    def __init__(self) -> None:
        self.calls: list[tuple[object, Path]] = []

    def run(self, run_config: object, base_wiki_dir: Path) -> None:
        self.calls.append((run_config, base_wiki_dir))


class _MergeSpy:
    def __init__(self) -> None:
        self.calls: list[Path] = []

    def merge(self, base_wiki_dir: Path) -> None:
        self.calls.append(base_wiki_dir)


def test_wiki_pipeline_facade_routes_common_scenarios(tmp_path: Path) -> None:
    layer_zero = _LayerExecutorSpy()
    layer_one = _LayerExecutorSpy()
    merge = _MergeSpy()
    facade = WikiPipelineFacade(
        base_wiki_dir=tmp_path / "wiki",
        base_debug_dir=tmp_path / "debug",
        layer_zero_executor=layer_zero,
        layer_one_executor=layer_one,
        layer_zero_merge_service=merge,
        run_config_factory=lambda: object(),
    )

    facade.run_scenario("layer0")
    facade.run_scenario("layer1")
    facade.run_scenario("merge")
    facade.run_scenario("full")

    assert len(layer_zero.calls) == EXPECTED_SCENARIO_RUNS
    assert len(layer_one.calls) == EXPECTED_SCENARIO_RUNS
    assert merge.calls == [tmp_path / "wiki"]
