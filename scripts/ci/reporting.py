from __future__ import annotations

import argparse
from dataclasses import dataclass
from enum import Enum
from typing import Any


class CiStatus(str, Enum):
    ok = "ok"
    warn = "warn"
    fail = "fail"


@dataclass(frozen=True)
class CiReport:
    check_name: str
    status: CiStatus
    summary: str
    recommendation: str
    details: tuple[str, ...] = ()


def resolve_status(count: int, warn_threshold: int, fail_threshold: int) -> CiStatus:
    if count >= fail_threshold:
        return CiStatus.fail
    if count >= warn_threshold:
        return CiStatus.warn
    return CiStatus.ok


def exit_code_for_status(status: CiStatus) -> int:
    return 1 if status == CiStatus.fail else 0


def split_csv(value: str) -> list[str]:
    return [part for part in value.split(",") if part]


def line_range(meta: dict[str, Any]) -> str:
    start = meta.get("start", 0)
    end = meta.get("end", 0)
    if start and end:
        return f"L{start}-L{end}"
    return "line ?"


def build_ci_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--report-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--warn-threshold", type=int, required=True)
    parser.add_argument("--fail-threshold", type=int, required=True)
    parser.add_argument("--base-sha", default="")
    parser.add_argument("--head-sha", default="")
    parser.add_argument("--changed-files", default="")
    parser.add_argument("--github-output", required=True)
    return parser


def _status_marker(status: CiStatus) -> str:
    if status == CiStatus.ok:
        return "✅"
    if status == CiStatus.warn:
        return "⚠️"
    return "❌"


def render_console_report(report: CiReport) -> str:
    lines = [
        f"[{report.check_name}] {_status_marker(report.status)} STATUS: {report.status.value.upper()}",
        f"[{report.check_name}] Summary: {report.summary}",
        f"[{report.check_name}] Recommendation: {report.recommendation}",
    ]
    for detail in report.details:
        lines.append(f"[{report.check_name}] Detail: {detail}")
    return "\n".join(lines)


def print_console_report(report: CiReport) -> None:
    print(render_console_report(report))
