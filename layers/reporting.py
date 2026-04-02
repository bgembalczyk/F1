from __future__ import annotations

import json
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timezone
from pathlib import Path
from time import perf_counter
from typing import Literal

LayerName = Literal["layer0", "layer1"]
StatusName = Literal["success", "skipped", "error"]


@dataclass(frozen=True)
class PipelineIssue:
    code: str
    module: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "module": self.module,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class LayerJobResult:
    name: str
    module: str
    status: StatusName
    output_path: str | None = None
    error_code: str | None = None
    error_detail: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "name": self.name,
            "module": self.module,
            "status": self.status,
            "output_path": self.output_path,
            "error_code": self.error_code,
            "error_detail": self.error_detail,
        }


@dataclass
class LayerRunSummary:
    layer: LayerName
    started_at_utc: str
    finished_at_utc: str | None = None
    duration_seconds: float | None = None
    jobs: list[LayerJobResult] = field(default_factory=list)

    def complete(self, *, finished_at_utc: str, duration_seconds: float) -> None:
        self.finished_at_utc = finished_at_utc
        self.duration_seconds = duration_seconds

    @property
    def total_jobs(self) -> int:
        return len(self.jobs)

    @property
    def successes(self) -> int:
        return sum(job.status == "success" for job in self.jobs)

    @property
    def skipped(self) -> int:
        return sum(job.status == "skipped" for job in self.jobs)

    @property
    def errors(self) -> int:
        return sum(job.status == "error" for job in self.jobs)

    @property
    def output_paths(self) -> list[str]:
        ordered: list[str] = []
        for job in self.jobs:
            if job.output_path is None:
                continue
            if job.output_path in ordered:
                continue
            ordered.append(job.output_path)
        return ordered

    @property
    def issues(self) -> list[PipelineIssue]:
        issues: list[PipelineIssue] = []
        for job in self.jobs:
            if job.status != "error":
                continue
            issues.append(
                PipelineIssue(
                    code=job.error_code or "E_UNKNOWN",
                    module=job.module,
                    detail=job.error_detail or "unknown",
                ),
            )
        return issues

    def to_dict(self) -> dict[str, object]:
        return {
            "layer": self.layer,
            "started_at_utc": self.started_at_utc,
            "finished_at_utc": self.finished_at_utc,
            "duration_seconds": self.duration_seconds,
            "counts": {
                "jobs": self.total_jobs,
                "successes": self.successes,
                "skipped": self.skipped,
                "errors": self.errors,
            },
            "output_paths": self.output_paths,
            "jobs_detail": [job.to_dict() for job in self.jobs],
            "co_poszlo_nie_tak": [issue.to_dict() for issue in self.issues],
        }


@dataclass(frozen=True)
class _RunTimer:
    started_at_utc: str
    started_counter: float


class RunSummaryBuilder:
    def start(self, *, layer: LayerName) -> tuple[LayerRunSummary, _RunTimer]:
        timer = _RunTimer(
            started_at_utc=datetime.now(tz=timezone.utc).isoformat(),
            started_counter=perf_counter(),
        )
        summary = LayerRunSummary(layer=layer, started_at_utc=timer.started_at_utc)
        return summary, timer

    def finish(self, summary: LayerRunSummary, timer: _RunTimer) -> LayerRunSummary:
        summary.complete(
            finished_at_utc=datetime.now(tz=timezone.utc).isoformat(),
            duration_seconds=round(perf_counter() - timer.started_counter, 3),
        )
        return summary


def write_pipeline_report(
    *,
    debug_dir: Path,
    mode: str,
    layer_summaries: list[LayerRunSummary],
) -> tuple[Path, Path]:
    debug_dir.mkdir(parents=True, exist_ok=True)

    combined_output_paths: list[str] = []
    issues: list[dict[str, str]] = []
    for summary in layer_summaries:
        for path in summary.output_paths:
            if path not in combined_output_paths:
                combined_output_paths.append(path)
        for issue in summary.issues:
            issues.append(issue.to_dict())

    report_payload = {
        "schema_version": "1.0",
        "mode": mode,
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "layers": [summary.to_dict() for summary in layer_summaries],
        "aggregate": {
            "jobs": sum(summary.total_jobs for summary in layer_summaries),
            "successes": sum(summary.successes for summary in layer_summaries),
            "skipped": sum(summary.skipped for summary in layer_summaries),
            "errors": sum(summary.errors for summary in layer_summaries),
            "duration_seconds": round(
                sum(summary.duration_seconds or 0.0 for summary in layer_summaries),
                3,
            ),
            "output_paths": combined_output_paths,
        },
        "co_poszlo_nie_tak": issues,
    }

    report_path = debug_dir / "wiki_pipeline_report.json"
    report_path.write_text(
        json.dumps(report_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    log_lines = [
        f"schema_version=1.0 mode={mode}",
        (
            "aggregate "
            f"jobs={report_payload['aggregate']['jobs']} "
            f"successes={report_payload['aggregate']['successes']} "
            f"skipped={report_payload['aggregate']['skipped']} "
            f"errors={report_payload['aggregate']['errors']} "
            f"duration_seconds={report_payload['aggregate']['duration_seconds']}"
        ),
        "output_paths",
        *[f"- {path}" for path in combined_output_paths],
        "co_poszlo_nie_tak",
        *[
            f"- {issue['code']} module={issue['module']} detail={issue['detail']}"
            for issue in issues
        ],
    ]
    log_path = debug_dir / "wiki_pipeline_report.log"
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    return report_path, log_path
