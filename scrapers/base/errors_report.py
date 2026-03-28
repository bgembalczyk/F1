import json
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from pathlib import Path

from scrapers.base.errors import ScraperError


@dataclass(frozen=True)
class ErrorReport:
    timestamp: str
    error_type: str
    message: str
    category: str | None
    behavior: str | None
    url: str | None
    section_id: str | None
    parser_name: str | None
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
        if isinstance(error, ScraperError):
            url = error.url
            section_id = error.section_id
            parser_name = error.parser_name
            category = error.category.value
            behavior = error.behavior.value
            critical = error.critical
            cause = error.cause
        else:
            url = None
            section_id = None
            parser_name = None
            category = None
            behavior = None
            critical = None
            cause = None
        return cls(
            timestamp=timestamp,
            error_type=type(error).__name__,
            message=str(error),
            category=category,
            behavior=behavior,
            url=url,
            section_id=section_id,
            parser_name=parser_name,
            critical=critical,
            cause_type=type(cause).__name__ if cause is not None else None,
            cause_message=str(cause) if cause is not None else None,
            run_id=run_id
            or (error.run_id if isinstance(error, ScraperError) else None),
        )


def write_error_report(debug_dir: Path, report: ErrorReport) -> Path:
    debug_dir.mkdir(parents=True, exist_ok=True)
    report_path = debug_dir / "errors.jsonl"
    with report_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(report), ensure_ascii=False))
        handle.write("\n")
    return report_path
