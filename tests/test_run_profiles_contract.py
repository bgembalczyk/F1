# ruff: noqa: S108
from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

from scrapers.base.cli_entrypoint import complete_extractor_base_config
from scrapers.base.cli_entrypoint import deprecated_module_base_config
from scrapers.base.domain_entrypoint import debug_profile
from scrapers.base.domain_entrypoint import default_profile
from scrapers.base.run_profiles import RunPathName
from scrapers.base.run_profiles import RunProfileName
from scrapers.base.run_profiles import build_run_profile
from scrapers.base.run_profiles import get_run_profile_spec

if TYPE_CHECKING:
    from pathlib import Path

    from scrapers.base.run_config import RunConfig


class _LayerExecutorSpy:
    def __init__(self) -> None:
        self.captured_configs: list[RunConfig] = []

    def run(self, run_config: RunConfig, _base_wiki_dir: Path) -> None:
        self.captured_configs.append(run_config)


def test_domain_entrypoint_profiles_match_central_definitions() -> None:
    assert default_profile() == build_run_profile(RunProfileName.DEFAULT)
    assert debug_profile() == build_run_profile(RunProfileName.DEBUG)


def test_legacy_wrappers_use_same_default_profile_as_ide_entrypoint() -> None:
    assert deprecated_module_base_config() == build_run_profile(
        RunProfileName.DEFAULT,
    )
    assert complete_extractor_base_config() == build_run_profile(RunProfileName.DEFAULT)


def test_domain_entrypoints_expose_stable_start_function() -> None:
    for module_path in (
        "scrapers.circuits.entrypoint",
        "scrapers.constructors.entrypoint",
        "scrapers.drivers.entrypoint",
        "scrapers.grands_prix.entrypoint",
        "scrapers.seasons.entrypoint",
    ):
        module = import_module(module_path)
        assert callable(module.run_list_scraper)


def test_profile_spec_exposes_explicit_configuration() -> None:
    default_spec = get_run_profile_spec(RunProfileName.DEFAULT)

    assert default_spec.name is RunProfileName.DEFAULT
    assert default_spec.output_dir is RunPathName.WIKI_OUTPUT_DIR
    assert default_spec.debug_dir is None
    assert default_spec.quality_report is False
    assert default_spec.error_report is False
