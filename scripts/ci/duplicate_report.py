from __future__ import annotations

import argparse
import json
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


def build_markdown(duplicates: list[dict[str, Any]], warn_threshold: int, fail_threshold: int) -> str:
    count = len(duplicates)
    status = "✅ Brak nowych duplikatów w zmienionych plikach."
    if count >= fail_threshold:
        status = (
            f"❌ Wykryto **{count}** nowych duplikatów (próg blokujący: {fail_threshold})."
        )
    elif count >= warn_threshold:
        status = (
            f"⚠️ Wykryto **{count}** nowych duplikatów (próg ostrzegawczy: {warn_threshold})."
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
            f"{idx}. `{first['name']}` ({_line_range(first)}) ↔ `{second['name']}` ({_line_range(second)})"
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
    parser.add_argument("--github-output", required=True)
    args = parser.parse_args()

    report_path = Path(args.report_json)
    if not report_path.exists():
        duplicates: list[dict[str, Any]] = []
    else:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        raw_duplicates = payload.get("duplicates") or payload.get("clones") or []
        duplicates = [_normalize_dup(item) for item in raw_duplicates]

    count = len(duplicates)
    markdown = build_markdown(duplicates, args.warn_threshold, args.fail_threshold)

    Path(args.output_md).write_text(markdown, encoding="utf-8")

    status = "ok"
    if count >= args.fail_threshold:
        status = "fail"
    elif count >= args.warn_threshold:
        status = "warn"

    output_path = Path(args.github_output)
    with output_path.open("a", encoding="utf-8") as fh:
        fh.write(f"duplicate_count={count}\n")
        fh.write(f"duplicate_status={status}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
