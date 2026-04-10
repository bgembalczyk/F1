from __future__ import annotations

from collections.abc import Callable
from typing import Any

from scrapers.orchestration.stages.envelope import StageEnvelope

LifecycleHook = Callable[[StageEnvelope], StageEnvelope]


class BaseComponent:
    """Technical base for stage-oriented components with lifecycle hooks."""

    def __init__(
        self,
        *,
        domain: str,
        stage: str,
        metadata: dict[str, Any] | None = None,
        errors: list[str] | None = None,
    ) -> None:
        self.domain = domain
        self.stage = stage
        self.metadata = metadata or {}
        self.errors = list(errors or [])
        self._before_hooks: list[LifecycleHook] = []
        self._after_hooks: list[LifecycleHook] = []
        self._error_hooks: list[LifecycleHook] = []

    def register_before_hook(self, hook: LifecycleHook) -> None:
        self._before_hooks.append(hook)

    def register_after_hook(self, hook: LifecycleHook) -> None:
        self._after_hooks.append(hook)

    def register_error_hook(self, hook: LifecycleHook) -> None:
        self._error_hooks.append(hook)

    def build_envelope(
        self,
        *,
        stage: str | None = None,
        records: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
        errors: list[str] | None = None,
    ) -> StageEnvelope:
        return StageEnvelope(
            domain=self.domain,
            stage=stage or self.stage,
            records=records or [],
            metadata=(self.metadata | (metadata or {})),
            errors=[*self.errors, *(errors or [])],
        )

    def run_hooks(
        self, hooks: list[LifecycleHook], payload: StageEnvelope
    ) -> StageEnvelope:
        current = payload
        for hook in hooks:
            current = hook(current)
        return current

    def run_with_lifecycle(
        self, runner: Callable[[StageEnvelope], StageEnvelope], payload: StageEnvelope
    ) -> StageEnvelope:
        prepared = self.run_hooks(self._before_hooks, payload)
        try:
            result = runner(prepared)
        except Exception as exc:  # noqa: BLE001
            error_payload = self.build_envelope(
                stage=prepared.stage,
                records=prepared.records,
                metadata=prepared.metadata,
                errors=[*prepared.errors, str(exc)],
            )
            return self.run_hooks(self._error_hooks, error_payload)
        return self.run_hooks(self._after_hooks, result)


__all__ = ["BaseComponent", "LifecycleHook", "StageEnvelope"]
