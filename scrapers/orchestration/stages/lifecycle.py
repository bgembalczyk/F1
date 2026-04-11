from __future__ import annotations

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


__all__ = [
    "STAGE_INGEST",
    "STAGE_NORMALIZE",
    "STAGE_MERGE",
    "STAGE_VALIDATE",
    "STAGE_EXPORT",
    "PIPELINE_LIFECYCLE",
]
