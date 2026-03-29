from pathlib import Path

from layers.pipeline import WikiPipelineApplication
from scrapers.base.run_config import RunConfig


class _LayerExecutorStub:
    def __init__(self) -> None:
        self.calls: list[tuple[RunConfig, Path]] = []

    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None:
        self.calls.append((run_config, base_wiki_dir))


def test_run_layer_zero_uses_private_run_config_builder(tmp_path: Path) -> None:
    base_wiki_dir = tmp_path / "wiki"
    base_debug_dir = tmp_path / "debug"
    layer_zero_executor = _LayerExecutorStub()
    layer_one_executor = _LayerExecutorStub()
    app = WikiPipelineApplication(
        base_wiki_dir=base_wiki_dir,
        base_debug_dir=base_debug_dir,
        layer_zero_executor=layer_zero_executor,
        layer_one_executor=layer_one_executor,
    )

    app.run_layer_zero()

    assert len(layer_zero_executor.calls) == 1
    run_config, base_wiki_dir = layer_zero_executor.calls[0]
    assert base_wiki_dir == app._base_wiki_dir  # noqa: SLF001
    assert run_config.output_dir == app._base_wiki_dir  # noqa: SLF001
    assert run_config.debug_dir == app._base_debug_dir  # noqa: SLF001


def test_run_layer_one_uses_private_run_config_builder(tmp_path: Path) -> None:
    base_wiki_dir = tmp_path / "wiki"
    base_debug_dir = tmp_path / "debug"
    layer_zero_executor = _LayerExecutorStub()
    layer_one_executor = _LayerExecutorStub()
    app = WikiPipelineApplication(
        base_wiki_dir=base_wiki_dir,
        base_debug_dir=base_debug_dir,
        layer_zero_executor=layer_zero_executor,
        layer_one_executor=layer_one_executor,
    )

    app.run_layer_one()

    assert len(layer_one_executor.calls) == 1
    run_config, base_wiki_dir = layer_one_executor.calls[0]
    assert base_wiki_dir == app._base_wiki_dir  # noqa: SLF001
    assert run_config.output_dir == app._base_wiki_dir  # noqa: SLF001
    assert run_config.debug_dir == app._base_debug_dir  # noqa: SLF001
