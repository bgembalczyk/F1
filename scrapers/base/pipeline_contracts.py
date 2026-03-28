from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from typing import Literal
from typing import TypeAlias

from models.mappers.serialization import to_dict

PipelineStageName: TypeAlias = Literal[
    "fetch",
    "parse",
    "normalize",
    "transform",
    "validate",
    "postprocess",
]


class PipelineContractError(TypeError):
    """Raised when a pipeline stage violates its input/output contract."""


def ensure_fetch_output(html: object) -> str:
    """Validate fetch stage output (must be HTML string)."""
    if isinstance(html, str):
        return html
    msg = f"Pipeline contract violation at fetch: expected str, got {type(html).__name__}"
    raise PipelineContractError(msg)


def ensure_records_output(
    stage: PipelineStageName,
    records: object,
) -> list[dict[str, Any]]:
    """Validate parse/normalize/transform/validate/postprocess stage outputs.

    The pipeline uses list-like record batches where each record must be serializable
    to dictionary form (mapping/dataclass/pydantic-like object).
    """
    if not isinstance(records, list):
        msg = (
            f"Pipeline contract violation at {stage}: "
            f"expected list, got {type(records).__name__}"
        )
        raise PipelineContractError(msg)

    for idx, record in enumerate(records):
        if isinstance(record, Mapping):
            continue
        try:
            to_dict(record)
        except TypeError as exc:
            msg = (
                f"Pipeline contract violation at {stage}[{idx}]: "
                f"record is not mapping/serializable ({type(record).__name__})"
            )
            raise PipelineContractError(msg) from exc

    return records
