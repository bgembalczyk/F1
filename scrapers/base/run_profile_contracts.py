from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from scrapers.base.run_profiles import RunPathConfig


@dataclass(frozen=True)
class BuildRunConfigRequestDTO:
    paths: Any

    def validate(self) -> None:
        if self.paths is None:
            msg = "paths cannot be None"
            raise TypeError(msg)
        if not hasattr(self.paths, "wiki_output_dir") or not hasattr(self.paths, "debug_dir"):
            msg = "paths must expose wiki_output_dir and debug_dir"
            raise TypeError(msg)

    def short(self) -> str:
        return (
            "BuildRunConfigRequestDTO("
            f"wiki_output_dir={self.paths.wiki_output_dir!s}, "
            f"debug_dir={self.paths.debug_dir!s})"
        )


@dataclass(frozen=True)
class BuildRunConfigResultDTO:
    run_config: Any

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

    def short(self) -> str:
        return (
            "BuildRunConfigResultDTO("
            f"output_dir={self.run_config.output_dir!s}, "
            f"include_urls={self.run_config.include_urls}, "
            f"debug_dir={self.run_config.debug_dir!s})"
        )
