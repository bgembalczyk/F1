import json
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from pathlib import Path


@dataclass(frozen=True)
class ErrorReport:
    timestamp: str
    error_type: str
    message: str
    url: str | None
    critical: bool | None
    cause_type: str | None = None
    cause_message: str | None = None
    run_id: str | None = None

    @classmethod
    def from_exception(
        cls,
        error: Exception,
        *,
        run_id: str | None = None,
    ) -> "ErrorReport":
        timestamp = datetime.now(timezone.utc).isoformat()
        url = getattr(error, "url", None)
        critical_attr = getattr(error, "critical", None)
        critical = critical_attr if isinstance(critical_attr, bool) else None
        cause = getattr(error, "cause", None)
        return cls(
            timestamp=timestamp,
            error_type=type(error).__name__,
            message=str(error),
            url=url,
            critical=critical,
            cause_type=type(cause).__name__ if cause is not None else None,
            cause_message=str(cause) if cause is not None else None,
            run_id=run_id,
        )


def write_error_report(debug_dir: Path, report: ErrorReport) -> Path:
    debug_dir.mkdir(parents=True, exist_ok=True)
    report_path = debug_dir / "errors.jsonl"
    with report_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(report), ensure_ascii=False))
        handle.write("\n")
    return report_path
