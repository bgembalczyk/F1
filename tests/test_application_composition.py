from pathlib import Path

from layers.composition import create_default_wiki_pipeline_application
from layers.executors.one import LayerOneExecutor
from layers.job_hooks.composite_zero import CompositeLayerZeroJobHook
from layers.job_hooks.mirror.constructors import MirrorConstructorsJobHook
from layers.pipeline import WikiPipelineApplication
from layers.zero.executor import LayerZeroExecutor


def test_default_application_is_wired_with_expected_components(tmp_path: Path) -> None:
    app = create_default_wiki_pipeline_application(
        base_wiki_dir=tmp_path / "wiki",
        base_debug_dir=tmp_path / "debug",
    )

    assert isinstance(app, WikiPipelineApplication)

    layer_zero_executor = app._layer_zero_executor
    layer_one_executor = app._layer_one_executor

    assert isinstance(layer_zero_executor, LayerZeroExecutor)
    assert isinstance(layer_one_executor, LayerOneExecutor)

    assert callable(layer_zero_executor._config_factories)
    assert layer_zero_executor._default_config_factory is not None
    assert layer_zero_executor._merger is not None
    composite_job_hook = layer_zero_executor._job_hook
    assert isinstance(composite_job_hook, CompositeLayerZeroJobHook)
    assert any(
        isinstance(hook, MirrorConstructorsJobHook) for hook in composite_job_hook.hooks
    )
    assert callable(layer_zero_executor._year_provider)

    assert callable(layer_one_executor._validate_seed_registry)
    assert callable(layer_one_executor._runners)
    assert callable(layer_one_executor._engine_manufacturers_runner)
