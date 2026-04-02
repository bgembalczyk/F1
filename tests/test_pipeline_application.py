from pathlib import Path

from layers.one.executor import LayerOneExecutor
from layers.orchestration.protocols import LayerExecutorProtocol
from layers.orchestration.runtime_config import RuntimeConfig
from layers.zero.executor import LayerZeroExecutor
from layers.pipeline import WikiPipelineApplication
from layers.zero.merge_service import LayerZeroMergeService
from layers.zero.policies import NullLayerZeroJobHook


class _LayerExecutorStub(LayerExecutorProtocol):
    def __init__(self) -> None:
        self.calls: list[RuntimeConfig] = []

    def run(self, runtime_config: RuntimeConfig) -> None:
        self.calls.append(runtime_config)


def test_pipeline_executor_protocol_is_implemented_by_production_executors() -> None:
    class _DefaultFactory:
        def create_scraper_kwargs(self, _job: object) -> dict[str, object]:
            return {}

    layer_zero = LayerZeroExecutor(
        list_job_registry=(),
        validate_list_registry=lambda _registry: None,
        run_config_factory_map_builder=dict,
        default_config_factory=_DefaultFactory(),
        merge_service=LayerZeroMergeService(merge_function=lambda _base_wiki_dir: None),
        job_hook=NullLayerZeroJobHook(),
        year_provider=lambda: 2026,
    )
    layer_one = LayerOneExecutor(
        seed_registry=(),
        validate_seed_registry_function=lambda _registry: None,
        runner_map_builder=dict,
        engine_manufacturers_runner=lambda *_args, **_kwargs: None,
    )

    assert isinstance(layer_zero, LayerExecutorProtocol)
    assert isinstance(layer_one, LayerExecutorProtocol)


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
    runtime_config = layer_zero_executor.calls[0]
    assert runtime_config.base_wiki_dir == app._base_wiki_dir  # noqa: SLF001
    assert runtime_config.base_debug_dir == app._base_debug_dir  # noqa: SLF001


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
    runtime_config = layer_one_executor.calls[0]
    assert runtime_config.base_wiki_dir == app._base_wiki_dir  # noqa: SLF001
    assert runtime_config.base_debug_dir == app._base_debug_dir  # noqa: SLF001
