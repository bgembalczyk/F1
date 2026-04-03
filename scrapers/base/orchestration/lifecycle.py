from __future__ import annotations

import json
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

STAGE_INGEST = "ingest"
STAGE_NORMALIZE = "normalize"
STAGE_MERGE = "merge"
STAGE_VALIDATE = "validate"
STAGE_EXPORT = "export"

PIPELINE_LIFECYCLE: tuple[str, ...] = (
    STAGE_INGEST,
    STAGE_NORMALIZE,
    STAGE_MERGE,
    STAGE_VALIDATE,
    STAGE_EXPORT,
)


@dataclass(frozen=True)
class StageEnvelope:
    """Minimalny kontrakt danych przekazywany pomiędzy etapami."""

    domain: str
    stage: str
    records: list[dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class PipelineStage(Protocol):
    """Jednolity interfejs etapu lifecycle."""

    name: str

    def run(self, payload: StageEnvelope) -> StageEnvelope: ...


class StageCheckpointDumper:
    """Opcjonalny dump po każdym etapie dla wybranych domen."""

    def __init__(
        self,
        *,
        checkpoints_dir: Path,
        enabled_domains: set[str] | None = None,
    ) -> None:
        self._checkpoints_dir = checkpoints_dir
        self._enabled_domains = enabled_domains or set()

    def dump(self, payload: StageEnvelope) -> Path | None:
        if self._enabled_domains and payload.domain not in self._enabled_domains:
            return None
        self._checkpoints_dir.mkdir(parents=True, exist_ok=True)
        dump_path = (
            self._checkpoints_dir / f"stage_{payload.stage}_{payload.domain}.json"
        )
        dump_path.write_text(
            json.dumps(
                {
                    "metadata": payload.metadata
                    | {"stage": payload.stage, "domain": payload.domain},
                    "records": payload.records,
                    "errors": payload.errors,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return dump_path
