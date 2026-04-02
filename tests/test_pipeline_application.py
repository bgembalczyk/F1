from pathlib import Path

from layers.reporting import LayerJobResult
from layers.reporting import LayerRunSummary
from layers.one.executor import LayerOneExecutor
from layers.orchestration.protocols import LayerExecutorProtocol
from layers.zero.executor import LayerZeroExecutor
from layers.pipeline import WikiPipelineApplication
from layers.zero.merge_service import LayerZeroMergeService
from layers.zero.policies import NullLayerZeroJobHook
from scrapers.base.run_config import RunConfig


class _LayerExecutorStub(LayerExecutorProtocol):
    def __init__(self) -> None:
        self.calls: list[tuple[RunConfig, Path]] = []
        self.last_summary: LayerRunSummary | None = None

    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None:
        self.calls.append((run_config, base_wiki_dir))


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


def test_write_summary_report_saves_single_stable_payload(tmp_path: Path) -> None:
    layer_zero_executor = _LayerExecutorStub()
    layer_one_executor = _LayerExecutorStub()
    layer_zero_executor.last_summary = LayerRunSummary(
        layer="layer0",
        started_at_utc="2026-01-01T00:00:00+00:00",
        finished_at_utc="2026-01-01T00:00:01+00:00",
        duration_seconds=1.0,
        jobs=[
            LayerJobResult(
                name="drivers",
                module="scrapers.drivers.list_scraper",
                status="success",
                output_path="/tmp/wiki/layers/0_layer/drivers/raw/f1_drivers_2026.json",
            ),
        ],
    )
    layer_one_executor.last_summary = LayerRunSummary(
        layer="layer1",
        started_at_utc="2026-01-01T00:00:02+00:00",
        finished_at_utc="2026-01-01T00:00:03+00:00",
        duration_seconds=1.0,
        jobs=[
            LayerJobResult(
                name="unknown_seed",
                module="layers.one.executor",
                status="error",
                error_code="L1_SEED_FAILED",
                error_detail="boom",
            ),
        ],
    )
    app = WikiPipelineApplication(
        base_wiki_dir=tmp_path / "wiki",
        base_debug_dir=tmp_path / "debug",
        layer_zero_executor=layer_zero_executor,
        layer_one_executor=layer_one_executor,
    )

    report_path, log_path = app.write_summary_report(mode="full")

    report = report_path.read_text(encoding="utf-8")
    log = log_path.read_text(encoding="utf-8")
    assert '"schema_version": "1.0"' in report
    assert '"co_poszlo_nie_tak"' in report
    assert '"jobs": 2' in report
    assert "aggregate jobs=2 successes=1 skipped=0 errors=1" in log
