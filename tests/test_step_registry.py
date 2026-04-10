from pathlib import Path

from layers.orchestration import STEP_REGISTRY
from layers.orchestration import list_wave_entries
from layers.orchestration import resolve_checkpoint_path


def test_step_registry_has_all_waves() -> None:
    assert {entry.wave for entry in STEP_REGISTRY} == {"A", "B", "C", "D"}


def test_step_registry_points_to_checkpoints() -> None:
    missing: list[str] = []
    root = Path(__file__).resolve().parent.parent
    for entry in STEP_REGISTRY:
        input_path = resolve_checkpoint_path(entry.checkpoint_input, repo_root=root)
        output_path = resolve_checkpoint_path(entry.checkpoint_output, repo_root=root)
        if not input_path.exists():
            missing.append(str(input_path))
        if not output_path.exists():
            missing.append(str(output_path))
    assert not missing


def test_wave_b_has_two_pilot_domains() -> None:
    wave_b_domains = {entry.domain for entry in list_wave_entries("B")}
    assert wave_b_domains == {"drivers", "constructors"}
