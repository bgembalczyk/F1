import json
from pathlib import Path

from scrapers.orchestration.stages.envelope import StageEnvelope


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
