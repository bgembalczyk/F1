from pathlib import Path

from layers.composition import create_default_wiki_pipeline_application
from layers.one.executor import LayerOneExecutor
from layers.pipeline import WikiPipelineApplication
from layers.zero.executor import LayerZeroExecutor
from layers.zero.policies import MirrorConstructorsJobHook


def test_default_application_is_wired_with_expected_components(tmp_path: Path) -> None:
    app = create_default_wiki_pipeline_application(
        base_wiki_dir=tmp_path / "wiki",
        base_debug_dir=tmp_path / "debug",
    )

    assert isinstance(app, WikiPipelineApplication)

    layer_zero_executor = app._layer_zero_executor  # noqa: SLF001
    layer_one_executor = app._layer_one_executor  # noqa: SLF001

    assert isinstance(layer_zero_executor, LayerZeroExecutor)
    assert isinstance(layer_one_executor, LayerOneExecutor)

    assert callable(layer_zero_executor._config_factories)  # noqa: SLF001
    assert layer_zero_executor._default_config_factory is not None  # noqa: SLF001
    assert layer_zero_executor._merger is not None  # noqa: SLF001
    assert isinstance(layer_zero_executor._job_hook, MirrorConstructorsJobHook)  # noqa: SLF001
    assert callable(layer_zero_executor._year_provider)  # noqa: SLF001

    assert callable(layer_one_executor._validate_seed_registry)  # noqa: SLF001
    assert callable(layer_one_executor._runners)  # noqa: SLF001
    assert callable(layer_one_executor._engine_manufacturers_runner)  # noqa: SLF001
