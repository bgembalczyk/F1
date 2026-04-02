from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from layers.zero.helpers import build_debug_run_config
from scrapers.base.run_config import RunConfig

WikiMode = Literal["layer0", "layer1", "full"]
RuntimeProfile = Literal["debug"]


@dataclass(frozen=True)
class RuntimeConfig:
    base_wiki_dir: Path
    base_debug_dir: Path
    mode: WikiMode = "layer0"
    include_urls: bool = True
    verbose: bool = False
    trace: bool = False
    profile: RuntimeProfile = "debug"

    def to_run_config(self) -> RunConfig:
        if self.profile != "debug":
            raise ValueError(self.profile)
        return dataclasses.replace(
            build_debug_run_config(
                base_wiki_dir=self.base_wiki_dir,
                base_debug_dir=self.base_debug_dir,
            ),
            include_urls=self.include_urls,
            verbose=self.verbose,
            trace=self.trace,
        )


def map_wiki_cli_to_runtime_config(
    *,
    base_wiki_dir: Path,
    base_debug_dir: Path,
    mode: WikiMode,
    include_urls: bool,
    verbose: bool,
    trace: bool,
) -> RuntimeConfig:
    return RuntimeConfig(
        base_wiki_dir=base_wiki_dir,
        base_debug_dir=base_debug_dir,
        mode=mode,
        include_urls=include_urls,
        verbose=verbose,
        trace=trace,
    )
