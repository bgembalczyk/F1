import json
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class TablePipelineDebugContext:
    url: str | None
    section_id: str | None
    header: str | None
    row_index: int | None
    run_id: str | None = None


def write_infobox_dump(
    debug_dir: Path,
    *,
    html: str,
    url: str | None,
    run_id: str | None = None,
) -> Path:
    debug_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_run_id = run_id or "unknown"
    filename = f"infobox_{safe_run_id}_{timestamp}.html"
    dump_path = debug_dir / filename
    dump_path.write_text(html, encoding="utf-8")
    return dump_path


def write_table_pipeline_dump(
    debug_dir: Path,
    *,
    context: TablePipelineDebugContext,
    cell_html: str | None,
    error: Exception | None = None,
) -> Path:
    debug_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"table_pipeline_{timestamp}_{uuid4().hex}.json"
    payload: dict[str, Any] = {
        "context": {
            "url": context.url,
            "section_id": context.section_id,
            "header": context.header,
            "row_index": context.row_index,
            "run_id": context.run_id,
        },
        "cell_html": cell_html,
    }
    if error is not None:
        payload["error"] = {
            "type": type(error).__name__,
            "message": str(error),
        }
    dump_path = debug_dir / filename
    dump_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    return dump_path
