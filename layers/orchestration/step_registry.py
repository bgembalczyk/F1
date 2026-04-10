from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final
from typing import Literal

WaveName = Literal["A", "B", "C", "D"]


@dataclass(frozen=True)
class StepRegistryEntry:
    """Deklaratywny wpis kroku migracji 0/1 z checkpointami startowymi."""

    step_id: str
    wave: WaveName
    layer: Literal["L0", "L1", "MIX"]
    domain: str
    parser: str
    checkpoint_input: str
    checkpoint_output: str


STEP_REGISTRY: Final[tuple[StepRegistryEntry, ...]] = (
    StepRegistryEntry(
        step_id="A-001",
        wave="A",
        layer="MIX",
        domain="foundation",
        parser="contracts+base_classes+mixins",
        checkpoint_input="data/checkpoints/stage_A_foundation_start.json",
        checkpoint_output="data/checkpoints/stage_A_foundation_ready.json",
    ),
    StepRegistryEntry(
        step_id="B-001",
        wave="B",
        layer="L0",
        domain="drivers",
        parser="drivers.seed.adapter",
        checkpoint_input="data/checkpoints/step_100_layer0_drivers_seed.json",
        checkpoint_output="data/checkpoints/step_110_layer1_drivers_complete.json",
    ),
    StepRegistryEntry(
        step_id="B-002",
        wave="B",
        layer="L0",
        domain="constructors",
        parser="constructors.seed.adapter",
        checkpoint_input="data/checkpoints/step_120_layer0_constructors_seed.json",
        checkpoint_output="data/checkpoints/step_130_layer1_constructors_complete.json",
    ),
    StepRegistryEntry(
        step_id="C-001",
        wave="C",
        layer="MIX",
        domain="rollout",
        parser="auto_registry+url_strategy",
        checkpoint_input="data/checkpoints/stage_C_rollout_start.json",
        checkpoint_output="data/checkpoints/stage_C_rollout_ready.json",
    ),
    StepRegistryEntry(
        step_id="D-001",
        wave="D",
        layer="MIX",
        domain="cleanup",
        parser="legacy_cleanup",
        checkpoint_input="data/checkpoints/stage_D_cleanup_start.json",
        checkpoint_output="data/checkpoints/stage_D_cleanup_done.json",
    ),
)


def resolve_checkpoint_path(relative_checkpoint: str, *, repo_root: Path) -> Path:
    """Zwraca absolutną ścieżkę checkpointu na podstawie wpisu `STEP_REGISTRY`."""

    return repo_root / relative_checkpoint


def list_wave_entries(wave: WaveName) -> tuple[StepRegistryEntry, ...]:
    """Filtruje wpisy registry do wskazanej fali migracyjnej."""

    return tuple(entry for entry in STEP_REGISTRY if entry.wave == wave)
