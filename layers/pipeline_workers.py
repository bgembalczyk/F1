from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from layers.zero.run_profile_paths import build_debug_run_config
from scrapers.base.run_config import RunConfig


@dataclass(frozen=True)
class RunConfigBuildInput:
    profile: str
    base_wiki_dir: Path
    base_debug_dir: Path


class RunConfigBuilderWorker:
    def build(self, data: RunConfigBuildInput) -> RunConfig:
        if data.profile == "debug":
            return build_debug_run_config(
                base_wiki_dir=data.base_wiki_dir,
                base_debug_dir=data.base_debug_dir,
            )
        raise ValueError(data.profile)
