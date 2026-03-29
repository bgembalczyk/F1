from __future__ import annotations

from pathlib import Path

from scrapers.base.orchestration.components.record_loader import RecordLoader
from scrapers.base.orchestration.components.source_path_resolver import SourcePathResolver
from scrapers.base.orchestration.models import OrchestrationPaths
from scrapers.base.orchestration.models import ResolvedInput
from scrapers.base.orchestration.models import StepDeclaration


class SectionSourceAdapter:
    """Thin orchestrator for source-path resolution and payload loading."""

    def __init__(
        self,
        base_dir: Path = Path("data"),
        fallback_order: tuple[str, ...] = ("checkpoint", "raw", "legacy"),
        source_path_resolver: SourcePathResolver | None = None,
        record_loader: RecordLoader | None = None,
    ) -> None:
        paths = OrchestrationPaths(base_dir=base_dir)
        self._source_path_resolver = source_path_resolver or SourcePathResolver(
            paths=paths,
            fallback_order=fallback_order,
        )
        self._record_loader = record_loader or RecordLoader()

    def resolve(self, step: StepDeclaration, domain: str) -> ResolvedInput:
        resolved_path = self._source_path_resolver.resolve(step, domain)
        if resolved_path is None:
            msg = (
                "Brak źródła wejścia dla "
                f"kroku={step.step_id}, source={step.input_source}"
            )
            raise FileNotFoundError(msg)
        return ResolvedInput(
            records=self._record_loader.load(resolved_path),
            source_path=resolved_path,
        )
