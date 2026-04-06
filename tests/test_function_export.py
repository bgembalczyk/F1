# ruff: noqa: E501, PLR2004
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from layers.orchestration.runners.function_export import FunctionExportRunner
from layers.orchestration.runners.metadata import build_runner_metadata
from scrapers.base.errors import PipelineError


METADATA = build_runner_metadata("test_domain", seed_name="test_seed")


def test_function_export_runner_raises_when_no_callable_provided() -> None:
    with pytest.raises(ValueError, match="requires `export` callable"):
        FunctionExportRunner(component_metadata=METADATA)


def test_function_export_runner_accepts_export_kwarg() -> None:
    fn = MagicMock()
    runner = FunctionExportRunner(export=fn, component_metadata=METADATA)
    assert runner._export is fn


def test_function_export_runner_accepts_export_function_kwarg() -> None:
    fn = MagicMock()
    runner = FunctionExportRunner(export_function=fn, component_metadata=METADATA)
    assert runner._export is fn


def test_function_export_runner_run_wraps_exception_in_pipeline_error() -> None:
    failing_fn = MagicMock(side_effect=RuntimeError("boom"))
    seed = MagicMock()
    seed.default_output_path = "drivers/output"
    seed.output_category = "drivers"
    run_config = MagicMock()
    run_config.include_urls = True

    runner = FunctionExportRunner(export=failing_fn, component_metadata=METADATA)

    with pytest.raises(PipelineError):
        runner.run(seed=seed, run_config=run_config, base_wiki_dir=Path("/wiki"))


def test_function_export_runner_run_passes_correct_args_on_success() -> None:
    fn = MagicMock()
    seed = MagicMock()
    seed.default_output_path = "drivers/output"
    seed.output_category = "drivers"
    run_config = MagicMock()
    run_config.include_urls = False

    runner = FunctionExportRunner(export=fn, component_metadata=METADATA)
    runner.run(seed=seed, run_config=run_config, base_wiki_dir=Path("/wiki"))

    fn.assert_called_once_with(
        output_dir=Path("/wiki/drivers/output"),
        include_urls=False,
    )
