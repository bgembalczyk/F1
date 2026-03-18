# ruff: noqa: S108, TC001
from __future__ import annotations

from pathlib import Path

from layers.pipeline import WikiPipelineApplication
from scrapers.base.cli_entrypoint import complete_extractor_base_config
from scrapers.base.cli_entrypoint import complete_extractor_run_config
from scrapers.base.cli_entrypoint import deprecated_module_base_config
from scrapers.base.domain_entrypoint import minimal_debug_profile
from scrapers.base.domain_entrypoint import minimal_profile
from scrapers.base.domain_entrypoint import strict_quality_profile
from scrapers.base.run_config import RunConfig
from scrapers.base.run_profiles import RunPathConfig
from scrapers.base.run_profiles import RunProfileName
from scrapers.base.run_profiles import build_run_profile


class _LayerExecutorSpy:
    def __init__(self) -> None:
        self.captured_configs: list[RunConfig] = []

    def run(self, run_config: RunConfig, _base_wiki_dir: Path) -> None:
        self.captured_configs.append(run_config)


def test_domain_entrypoint_profiles_match_central_definitions() -> None:
    assert strict_quality_profile() == build_run_profile(RunProfileName.STRICT)
    assert minimal_profile() == build_run_profile(RunProfileName.MINIMAL)
    assert minimal_debug_profile() == build_run_profile(RunProfileName.DEBUG)


def test_cli_entrypoint_profiles_match_central_definitions() -> None:
    assert deprecated_module_base_config() == build_run_profile(
        RunProfileName.DEPRECATED,
    )
    assert complete_extractor_run_config() == build_run_profile(RunProfileName.MINIMAL)
    assert complete_extractor_base_config() == complete_extractor_run_config()


def test_wiki_application_uses_central_debug_profile_for_layer_runs() -> None:
    layer_zero = _LayerExecutorSpy()
    layer_one = _LayerExecutorSpy()
    base_wiki_dir = Path("/tmp/wiki")
    base_debug_dir = Path("/tmp/debug")

    app = WikiPipelineApplication(
        base_wiki_dir=base_wiki_dir,
        base_debug_dir=base_debug_dir,
        layer_zero_executor=layer_zero,
        layer_one_executor=layer_one,
    )

    app.run_layer_zero()
    app.run_layer_one()

    expected = build_run_profile(
        RunProfileName.DEBUG,
        paths=RunPathConfig(wiki_output_dir=base_wiki_dir, debug_dir=base_debug_dir),
    )
    assert layer_zero.captured_configs == [expected]
    assert layer_one.captured_configs == [expected]
