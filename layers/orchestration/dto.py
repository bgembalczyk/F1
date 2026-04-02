from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from layers.orchestration.protocols import LayerOneRunnerProtocol
from layers.orchestration.protocols import LayerZeroRunConfigFactoryProtocol
from scrapers.base.run_config import RunConfig


def _require_non_empty(value: str, *, field_name: str) -> str:
    if not value.strip():
        msg = f"{field_name} must be a non-empty string."
        raise ValueError(msg)
    return value


@dataclass(frozen=True, slots=True)
class ExecutionContextDto:
    run_id: str
    seed_name: str
    domain: str
    source_name: str

    def __post_init__(self) -> None:
        _require_non_empty(self.run_id, field_name="run_id")
        _require_non_empty(self.seed_name, field_name="seed_name")
        _require_non_empty(self.domain, field_name="domain")
        _require_non_empty(self.source_name, field_name="source_name")

    def to_log_payload(self) -> dict[str, str]:
        return {
            "run_id": self.run_id,
            "seed_name": self.seed_name,
            "domain": self.domain,
            "source_name": self.source_name,
        }


@dataclass(frozen=True, slots=True)
class LayerExecutionInputDto:
    run_config: RunConfig
    base_wiki_dir: Path

    def __post_init__(self) -> None:
        if not isinstance(self.base_wiki_dir, Path):
            msg = "base_wiki_dir must be a pathlib.Path instance."
            raise TypeError(msg)


@dataclass(frozen=True, slots=True)
class LayerZeroConfigFactoriesDto:
    entries: Mapping[str, LayerZeroRunConfigFactoryProtocol]

    @classmethod
    def from_mapping(
        cls,
        mapping: Mapping[str, LayerZeroRunConfigFactoryProtocol],
    ) -> LayerZeroConfigFactoriesDto:
        for seed_name, factory in mapping.items():
            _require_non_empty(seed_name, field_name="seed_name")
            if not isinstance(factory, LayerZeroRunConfigFactoryProtocol):
                msg = "Every config factory must implement LayerZeroRunConfigFactoryProtocol."
                raise TypeError(msg)
        return cls(entries=dict(mapping))

    def resolve_for_seed(
        self,
        seed_name: str,
        *,
        default_factory: LayerZeroRunConfigFactoryProtocol,
    ) -> LayerZeroRunConfigFactoryProtocol:
        return self.entries.get(seed_name, default_factory)


@dataclass(frozen=True, slots=True)
class LayerOneRunnersDto:
    entries: Mapping[str, LayerOneRunnerProtocol]

    @classmethod
    def from_mapping(
        cls,
        mapping: Mapping[str, LayerOneRunnerProtocol],
    ) -> LayerOneRunnersDto:
        for seed_name, runner in mapping.items():
            _require_non_empty(seed_name, field_name="seed_name")
            if not isinstance(runner, LayerOneRunnerProtocol):
                msg = "Every runner must implement LayerOneRunnerProtocol."
                raise TypeError(msg)
        return cls(entries=dict(mapping))

    def get(self, seed_name: str) -> LayerOneRunnerProtocol | None:
        return self.entries.get(seed_name)

