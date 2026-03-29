from pathlib import Path
from enum import Enum
from typing import Callable

from layers.one.executor import LayerOneExecutor
from layers.zero.executor import LayerZeroExecutor
from scrapers.base.run_config import RunConfig
from scrapers.base.run_profiles import RunPathConfig
from scrapers.base.run_profiles import RunProfileName
from scrapers.base.run_profiles import build_run_profile


class RunProfile(str, Enum):
    DEBUG = "debug"
    PROD = "prod"
    CI = "ci"


class WikiPipelineApplication:
    def __init__(
        self,
        *,
        base_wiki_dir: Path,
        base_debug_dir: Path,
        layer_zero_executor: LayerZeroExecutor,
        layer_one_executor: LayerOneExecutor,
    ) -> None:
        self._base_wiki_dir = base_wiki_dir
        self._base_debug_dir = base_debug_dir
        self._layer_zero_executor = layer_zero_executor
        self._layer_one_executor = layer_one_executor

    def _build_profile_run_config(self, *, profile_name: RunProfileName) -> RunConfig:
        return build_run_profile(
            profile_name,
            paths=RunPathConfig(
                wiki_output_dir=self._base_wiki_dir,
                debug_dir=self._base_debug_dir,
            ),
        )

    def _build_debug_run_config(self) -> RunConfig:
        return self._build_profile_run_config(profile_name=RunProfileName.DEBUG)

    def _build_prod_run_config(self) -> RunConfig:
        return self._build_profile_run_config(profile_name=RunProfileName.MINIMAL)

    def _build_ci_run_config(self) -> RunConfig:
        return self._build_profile_run_config(profile_name=RunProfileName.STRICT)

    def _build_run_config(self, *, profile: RunProfile = RunProfile.DEBUG) -> RunConfig:
        profile_builders: dict[RunProfile, Callable[[], RunConfig]] = {
            RunProfile.DEBUG: self._build_debug_run_config,
            RunProfile.PROD: self._build_prod_run_config,
            RunProfile.CI: self._build_ci_run_config,
        }
        return profile_builders[profile]()

    def run_layer_zero(self) -> None:
        run_config = self._build_run_config()
        self._layer_zero_executor.run(run_config, self._base_wiki_dir)

    def run_layer_one(self) -> None:
        run_config = self._build_run_config()
        self._layer_one_executor.run(run_config, self._base_wiki_dir)
