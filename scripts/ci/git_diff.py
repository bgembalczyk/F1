from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from typing import Any

_HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def build_added_lines_map(
    base_sha: str,
    head_sha: str,
    changed_files: list[str],
    *,
    run_command: Callable[..., Any] = subprocess.run,
) -> dict[str, set[int]]:
    if not base_sha or not head_sha or not changed_files:
        return {}

    diff_cmd = [
        "git",
        "diff",
        "--unified=0",
        "--no-color",
        base_sha,
        head_sha,
        "--",
        *changed_files,
    ]
    proc = run_command(
        diff_cmd,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return {}

    added: dict[str, set[int]] = {}
    current_file: str | None = None

    for raw_line in proc.stdout.splitlines():
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
