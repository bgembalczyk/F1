import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scrapers.base.orchestration.models import OrchestrationPaths
from scrapers.base.orchestration.models import ResolvedInput
from scrapers.base.orchestration.models import StepDeclaration


@dataclass(frozen=True)
class SourceSelectionRule:
    source: str
    pattern: str
    priority: int


@dataclass(frozen=True)
class SourceSelectionPolicy:
    priorities: tuple[str, ...]
    rules: tuple[SourceSelectionRule, ...]
    tie_breaker: str


SOURCE_SELECTION_POLICY = SourceSelectionPolicy(
    priorities=("checkpoint", "raw"),
    rules=(
        SourceSelectionRule(
            source="checkpoint",
            pattern="*{input_source}*{domain}*.json",
            priority=1,
        ),
        SourceSelectionRule(
            source="checkpoint",
            pattern="step_*_{layer}_{domain}.json",
            priority=2,
        ),
        SourceSelectionRule(
            source="raw",
            pattern="**/*{domain}*.json",
            priority=1,
        ),
    ),
    tie_breaker=(
        "Najpierw numer kroku (step_<N>), potem mtime (najnowszy), "
        "na końcu ścieżka leksykograficznie."
    ),
)


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

        resolvers = {
            "checkpoint": self._resolve_checkpoint,
            "raw": self._resolve_raw,
        }
        for source in SOURCE_SELECTION_POLICY.priorities:
            resolved = resolvers[source](step, domain)
            if resolved is not None:
                return resolved
        return None

    def _resolve_checkpoint(self, step: StepDeclaration, domain: str) -> Path | None:
        checkpoints_dir = self.paths.checkpoints
        explicit = checkpoints_dir / f"{step.input_source}.json"
        if explicit.exists():
            return explicit

        for rule in self._rules_for("checkpoint"):
            matches = list(
                checkpoints_dir.glob(
                    rule.pattern.format(
                        input_source=step.input_source,
                        domain=domain,
                        layer=step.layer,
                    )
                )
            )
            selected = self._select_best_match(matches)
            if selected is not None:
                return selected
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

        for rule in self._rules_for("raw"):
            matches = list(
                raw_dir.glob(
                    rule.pattern.format(
                        input_source=step.input_source,
                        domain=domain,
                        layer=step.layer,
                    )
                )
            )
            selected = self._select_best_match(matches)
            if selected is not None:
                return selected
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

    @staticmethod
    def _rules_for(source: str) -> list[SourceSelectionRule]:
        return sorted(
            [rule for rule in SOURCE_SELECTION_POLICY.rules if rule.source == source],
            key=lambda rule: rule.priority,
        )

    @staticmethod
    def _step_number(path: Path) -> int:
        match = re.search(r"step_(\d+)", path.name)
        return int(match.group(1)) if match else -1

    def _select_best_match(self, matches: list[Path]) -> Path | None:
        if not matches:
            return None
        return max(
            matches,
            key=lambda candidate: (
                self._step_number(candidate),
                candidate.stat().st_mtime_ns,
                str(candidate),
            ),
        )
