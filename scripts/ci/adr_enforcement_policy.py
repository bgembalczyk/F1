from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True)
class AdrEnforcementPolicy:
    """Shared ADR policy for architecture and DI-related CI checks."""

    architecture_prefixes: tuple[str, ...] = (
        "layers/",
        "scrapers/base/",
        "tests/architecture/",
    )
    adr_pattern: re.Pattern[str] = re.compile(r"\bADR-\d{4}\b", re.IGNORECASE)
    di_required_violation_threshold: int = 3

    def is_architecture_path(self, path: str) -> bool:
        normalized = PurePosixPath(path).as_posix()
        return any(
            normalized.startswith(prefix) for prefix in self.architecture_prefixes
        )

    def is_cosmetic_line(self, content: str) -> bool:
        stripped = content.strip()
        return not stripped or stripped.startswith("#")

    def should_require_adr_for_architecture_diff(
        self,
        *,
        has_architecture_changes: bool,
        has_non_cosmetic_changes: bool,
    ) -> bool:
        return has_architecture_changes and has_non_cosmetic_changes

    def should_emit_di_trigger_signal(
        self,
        violation_count: int,
        threshold: int | None = None,
    ) -> bool:
        required_threshold = (
            threshold if threshold is not None else self.di_required_violation_threshold
        )
        return violation_count >= required_threshold


DEFAULT_ADR_ENFORCEMENT_POLICY = AdrEnforcementPolicy()
