from __future__ import annotations

from pathlib import Path

from scrapers.base.orchestration.models import OrchestrationPaths
from scrapers.base.orchestration.models import StepDeclaration

ResolverName = str


class SourcePathResolver:
    """Resolves input path using configurable fallback order."""

    def __init__(
        self,
        paths: OrchestrationPaths,
        fallback_order: tuple[ResolverName, ...] = ("checkpoint", "raw", "legacy"),
    ) -> None:
        self._paths = paths
        self._fallback_order = fallback_order

    def resolve(self, step: StepDeclaration, domain: str) -> Path | None:
        direct_path = Path(step.input_source)
        if direct_path.is_absolute() and direct_path.exists():
            return direct_path

        for resolver_name in self._fallback_order:
            resolver = self._resolver_by_name(resolver_name)
            resolved = resolver(step, domain)
            if resolved is not None:
                return resolved
        return None

    def _resolver_by_name(self, name: ResolverName):
        resolvers = {
            "checkpoint": self._resolve_checkpoint,
            "raw": self._resolve_raw,
            "legacy": self._resolve_legacy,
        }
        if name not in resolvers:
            msg = f"Unsupported source resolver: {name!r}"
            raise ValueError(msg)
        return resolvers[name]

    def _resolve_checkpoint(self, step: StepDeclaration, domain: str) -> Path | None:
        checkpoints_dir = self._paths.checkpoints
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
        raw_dir = self._paths.raw
        candidates = [
            raw_dir / f"{step.input_source}.json",
            raw_dir / domain / f"{step.input_source}.json",
            raw_dir / domain / f"{domain}.json",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate

        matches = sorted(raw_dir.glob(f"**/*{domain}*.json"))
        if matches:
            return matches[-1]
        return None

    def _resolve_legacy(self, step: StepDeclaration, domain: str) -> Path | None:
        legacy_dir = self._paths.legacy_wiki / domain
        candidates = [
            legacy_dir / f"{step.input_source}.json",
            legacy_dir / f"{domain}.json",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None
