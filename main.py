from pathlib import Path

from pipeline.orchestrator import PipelineOrchestrator
from pipeline.step_registry import get_all_steps
from pipeline.step_registry import get_layer0_steps
from pipeline.step_registry import get_layer1_steps

CHECKPOINT_DIR = Path("data/checkpoints").resolve()


def run_list_scrapers() -> None:
    PipelineOrchestrator(
        steps=get_layer0_steps(),
        checkpoint_dir=CHECKPOINT_DIR,
    ).run()


def run_complete_scrapers() -> None:
    PipelineOrchestrator(
        steps=get_layer1_steps(),
        checkpoint_dir=CHECKPOINT_DIR,
    ).run()


def main() -> None:
    PipelineOrchestrator(
        steps=get_all_steps(),
        checkpoint_dir=CHECKPOINT_DIR,
    ).run()


if __name__ == "__main__":
    main()
