import json
from collections import Counter
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from pathlib import Path

from scrapers.base.error_codes import resolve_error_code
from scrapers.base.errors import ScraperError


@dataclass(frozen=True)
class ErrorReport:
    timestamp: str
    error_type: str
    code: str | None
    code_id: str
    code_description: str
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
        code = error.code if isinstance(error, ScraperError) else None
        code_definition = resolve_error_code(code)
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
            code=code,
            code_id=code_definition.code_id,
            code_description=code_definition.short_description,
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


def write_error_summary_by_code(
    debug_dir: Path,
    *,
    run_id: str | None = None,
) -> Path:
    report_path = debug_dir / "errors.jsonl"
    summary_path = debug_dir / "errors_summary_by_code.json"
    if not report_path.exists():
        summary_path.write_text(
            json.dumps(
                {
                    "run_id": run_id,
                    "total_errors": 0,
                    "error_counts_by_code": {},
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return summary_path

    code_counter: Counter[str] = Counter()
    for line in report_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if run_id is not None and payload.get("run_id") != run_id:
            continue
        code_id = str(payload.get("code_id") or "U000")
        code_counter[code_id] += 1

    summary_path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "total_errors": sum(code_counter.values()),
                "error_counts_by_code": dict(sorted(code_counter.items())),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return summary_path
