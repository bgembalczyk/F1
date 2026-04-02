from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LayerExecutionRequestDTO:
    run_config: Any
    base_wiki_dir: Path

    def validate(self) -> None:
        if self.run_config is None:
            msg = "run_config cannot be None"
            raise TypeError(msg)
        if not hasattr(self.run_config, "output_dir") or not hasattr(
            self.run_config,
            "include_urls",
        ):
            msg = "run_config must expose output_dir and include_urls"
            raise TypeError(msg)
        if not isinstance(self.base_wiki_dir, Path):
            msg = "base_wiki_dir must be Path"
            raise TypeError(msg)

    def short(self) -> str:
        return (
            "LayerExecutionRequestDTO("
            f"output_dir={self.run_config.output_dir!s}, "
            f"include_urls={self.run_config.include_urls}, "
            f"base_wiki_dir={self.base_wiki_dir!s})"
        )


@dataclass(frozen=True)
class LayerExecutionResultDTO:
    processed_jobs: int

    def short(self) -> str:
        return f"LayerExecutionResultDTO(processed_jobs={self.processed_jobs})"


@dataclass(frozen=True)
class LayerZeroMergeRequestDTO:
    base_wiki_dir: Path

    def validate(self) -> None:
        if not isinstance(self.base_wiki_dir, Path):
            msg = "base_wiki_dir must be Path"
            raise TypeError(msg)

    def short(self) -> str:
        return f"LayerZeroMergeRequestDTO(base_wiki_dir={self.base_wiki_dir!s})"


@dataclass(frozen=True)
class LayerZeroMergeResultDTO:
    merged: bool = True

    def short(self) -> str:
        return f"LayerZeroMergeResultDTO(merged={self.merged})"
