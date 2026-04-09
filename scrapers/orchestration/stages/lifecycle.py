from __future__ import annotations

import json
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol

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







__all__ = [
    "STAGE_INGEST",
    "STAGE_NORMALIZE",
    "STAGE_MERGE",
    "STAGE_VALIDATE",
    "STAGE_EXPORT",
    "PIPELINE_LIFECYCLE",
]
