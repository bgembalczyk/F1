import json
from pathlib import Path
from typing import Any

from scrapers.base.orchestration.models import OrchestrationPaths
from scrapers.base.orchestration.models import ResolvedInput
from scrapers.base.orchestration.models import StepDeclaration


class SectionSourceAdapter:
    """Pobiera wejście dla kroku z checkpointów i fallbackiem do raw."""

    def __init__(self, base_dir: Path = Path("data")) -> None:
        self.paths = OrchestrationPaths(base_dir=base_dir)

    def resolve(self, step: StepDeclaration, domain: str) -> ResolvedInput:
        resolved_path = self._resolve_source_path(step, domain)
        if resolved_path is None:
            msg = (
                "Brak źródła wejścia dla "
                f"kroku={step.step_id}, source={step.input_source}"
            )
            raise FileNotFoundError(msg)
        return ResolvedInput(
            records=self._read_records(resolved_path),
            source_path=resolved_path,
        )

    def _resolve_source_path(self, step: StepDeclaration, domain: str) -> Path | None:
        direct_path = Path(step.input_source)
        if direct_path.is_absolute() and direct_path.exists():
            return direct_path

        for resolver in (self._resolve_checkpoint, self._resolve_raw):
            resolved = resolver(step, domain)
            if resolved is not None:
                return resolved
        return None

    def _resolve_checkpoint(self, step: StepDeclaration, domain: str) -> Path | None:
        checkpoints_dir = self.paths.checkpoints
        explicit = checkpoints_dir / f"{step.input_source}.json"
        if explicit.exists():
            return explicit

        matches = sorted(checkpoints_dir.glob(f"*{step.input_source}*{domain}*.json"))
        if matches:
            return matches[-1]

        matches = sorted(checkpoints_dir.glob(f"step_*_{step.layer}_{domain}.json"))
        if matches:
            return matches[-1]
        return None

    def _resolve_raw(self, step: StepDeclaration, domain: str) -> Path | None:
        raw_dir = self.paths.raw
        candidates = [
            raw_dir / f"{step.input_source}.json",
            raw_dir / domain / f"{step.input_source}.json",
            raw_dir / domain / f"{domain}.json",
            self.paths.legacy_wiki / domain / f"{step.input_source}.json",
            self.paths.legacy_wiki / domain / f"{domain}.json",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate

        matches = sorted(raw_dir.glob(f"**/*{domain}*.json"))
        if matches:
            return matches[-1]
        return None

    @staticmethod
    def _read_records(path: Path) -> list[dict[str, Any]]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            records = payload.get("records", [])
            if isinstance(records, list):
                return [item for item in records if isinstance(item, dict)]
        return []
