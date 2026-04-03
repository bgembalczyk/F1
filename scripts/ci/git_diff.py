from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any

_HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
GIT_BIN = shutil.which("git") or "git"


@dataclass(frozen=True)
class GitCommandResult:
    returncode: int
    stdout: str


def _run_git_and_capture_stdout(args: list[str]) -> GitCommandResult:
    proc = subprocess.run(  # nosec B603 -- zaufane wywołanie lokalnego `git`
        [GIT_BIN, *args],
        check=False,
        capture_output=True,
        text=True,
    )
    return GitCommandResult(returncode=proc.returncode, stdout=proc.stdout or "")


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def parse_added_lines_from_unified_diff(diff_text: str) -> dict[str, set[int]]:
    """Parse `git diff --unified=0` output into a file->added line numbers map."""
    added: dict[str, set[int]] = {}
    current_file: str | None = None

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("+++ b/"):
            current_file = raw_line[6:]
            added.setdefault(current_file, set())
            continue

        if not raw_line.startswith("@@") or not current_file:
            continue

        match = _HUNK_RE.match(raw_line)
        if not match:
            continue

        start = _as_int(match.group(1))
        count = _as_int(match.group(2) or 1)
        if count <= 0:
            continue

        for line_no in range(start, start + count):
            added[current_file].add(line_no)

    return added


def build_added_lines_map(
    base_sha: str,
    head_sha: str,
    changed_files: list[str],
) -> dict[str, set[int]]:
    """Get added lines by parsing git diff for provided SHA range and file list."""
    if not base_sha or not head_sha or not changed_files:
        return {}

    diff_result = get_unified_diff(base_sha, head_sha, changed_files)
    if diff_result.returncode != 0:
        return {}

    return parse_added_lines_from_unified_diff(diff_result.stdout)


def list_changed_files(base_sha: str, head_sha: str) -> list[str]:
    if not base_sha or not head_sha:
        return []

    result = _run_git_and_capture_stdout(
        [
            "diff",
            "--name-only",
            "--diff-filter=ACMR",
            base_sha,
            head_sha,
        ],
    )
    if result.returncode != 0:
        return []

    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def collect_commit_messages(base_sha: str, head_sha: str) -> str:
    if not base_sha or not head_sha:
        return ""

    result = _run_git_and_capture_stdout(
        ["log", "--format=%B", f"{base_sha}..{head_sha}"],
    )
    if result.returncode != 0:
        return ""

    return result.stdout


def get_unified_diff(
    base_sha: str,
    head_sha: str,
    changed_files: list[str],
) -> GitCommandResult:
    if not base_sha or not head_sha:
        return GitCommandResult(returncode=1, stdout="")
    if not changed_files:
        return GitCommandResult(returncode=0, stdout="")

    return _run_git_and_capture_stdout(
        [
            "diff",
            "--unified=0",
            "--no-color",
            base_sha,
            head_sha,
            "--",
            *changed_files,
        ],
    )
