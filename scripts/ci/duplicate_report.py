# ruff: noqa: INP001, S603
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


def _normalize_dup(item: dict[str, Any]) -> dict[str, Any]:
    first = item.get("firstFile", {})
    second = item.get("secondFile", {})
    fragment = item.get("fragment") or item.get("codefragment") or ""
    return {
        "first": {
            "name": first.get("name") or first.get("path") or "<unknown>",
            "start": first.get("start") or first.get("startLoc") or 0,
            "end": first.get("end") or first.get("endLoc") or 0,
        },
        "second": {
            "name": second.get("name") or second.get("path") or "<unknown>",
            "start": second.get("start") or second.get("startLoc") or 0,
            "end": second.get("end") or second.get("endLoc") or 0,
        },
        "fragment": str(fragment).strip(),
    }


def _line_range(meta: dict[str, Any]) -> str:
    start = meta.get("start", 0)
    end = meta.get("end", 0)
    if start and end:
        return f"L{start}-L{end}"
    return "line ?"


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _build_added_lines_map(
    base_sha: str,
    head_sha: str,
    changed_files: list[str],
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
    proc = subprocess.run(  # noqa: S603
        diff_cmd,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return {}

    added: dict[str, set[int]] = {}
    current_file: str | None = None
    hunk_re = re.compile(r"^@@ -\\d+(?:,\\d+)? \\+(\\d+)(?:,(\\d+))? @@")

    for raw_line in proc.stdout.splitlines():
        if raw_line.startswith("+++ b/"):
            current_file = raw_line[6:]
            added.setdefault(current_file, set())
            continue

        if not raw_line.startswith("@@") or not current_file:
            continue

        match = hunk_re.match(raw_line)
        if not match:
            continue

        start = _as_int(match.group(1))
        count = _as_int(match.group(2) or 1)
        if count <= 0:
            continue

        for line_no in range(start, start + count):
            added[current_file].add(line_no)

    return added


def _is_new_duplicate(
    duplicate: dict[str, Any],
    added_lines: dict[str, set[int]],
) -> bool:
    for side in ("first", "second"):
        file_meta = duplicate[side]
        file_name = str(file_meta.get("name", ""))
        start = _as_int(file_meta.get("start"))
        end = _as_int(file_meta.get("end"))
        if not file_name or start <= 0 or end <= 0:
            continue

        changed_line_set = added_lines.get(file_name, set())
        if not changed_line_set:
            continue

        for line_no in range(start, end + 1):
            if line_no in changed_line_set:
                return True
    return False


def build_markdown(
    duplicates: list[dict[str, Any]],
    warn_threshold: int,
    fail_threshold: int,
) -> str:
    count = len(duplicates)
    status = "✅ Brak nowych duplikatów w zmienionych plikach."
    if count >= fail_threshold:
        status = (
            f"❌ Wykryto **{count}** nowych duplikatów "
            f"(próg blokujący: {fail_threshold})."
        )
    elif count >= warn_threshold:
        status = (
            f"⚠️ Wykryto **{count}** nowych duplikatów "
            f"(próg ostrzegawczy: {warn_threshold})."
        )

    lines = [
        "## Raport duplikatów (jscpd)",
        "",
        status,
        "",
        (
            "Analiza obejmuje tylko pliki Python zmienione w tym PR "
            "(dług historyczny jest pomijany na etapie startowym)."
        ),
        "",
    ]

    if not duplicates:
        return "\n".join(lines)

    lines.append("### Lista duplikatów")
    lines.append("")

    for idx, dup in enumerate(duplicates, start=1):
        first = dup["first"]
        second = dup["second"]
        lines.append(
            f"{idx}. `{first['name']}` ({_line_range(first)}) "
            f"↔ `{second['name']}` ({_line_range(second)})",
        )
        if dup["fragment"]:
            snippet = dup["fragment"][:400]
            lines.append("   ```python")
            lines.extend(f"   {line}" for line in snippet.splitlines())
            lines.append("   ```")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--warn-threshold", type=int, required=True)
    parser.add_argument("--fail-threshold", type=int, required=True)
    parser.add_argument("--base-sha", default="")
    parser.add_argument("--head-sha", default="")
    parser.add_argument("--changed-files", default="")
    parser.add_argument("--github-output", required=True)
    args = parser.parse_args()

    report_path = Path(args.report_json)
    if not report_path.exists():
        duplicates: list[dict[str, Any]] = []
    else:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        raw_duplicates = payload.get("duplicates") or payload.get("clones") or []
        duplicates = [_normalize_dup(item) for item in raw_duplicates]

    changed_files = [part for part in args.changed_files.split(",") if part]
    added_lines_map = _build_added_lines_map(
        args.base_sha,
        args.head_sha,
        changed_files,
    )
    if changed_files and not added_lines_map:
        new_duplicates = duplicates
    else:
        new_duplicates = [
            dup for dup in duplicates if _is_new_duplicate(dup, added_lines_map)
        ]

    count = len(new_duplicates)
    markdown = build_markdown(new_duplicates, args.warn_threshold, args.fail_threshold)

    output_md_path = Path(args.output_md)
    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    output_md_path.write_text(markdown, encoding="utf-8")

    status = "ok"
    if count >= args.fail_threshold:
        status = "fail"
    elif count >= args.warn_threshold:
        status = "warn"

    output_path = Path(args.github_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as fh:
        fh.write(f"duplicate_count={count}\n")
        fh.write(f"duplicate_status={status}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
