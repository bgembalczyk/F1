# ruff: noqa: S603
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.ci.git_diff import build_added_lines_map


class DuplicateNormalizer:
    def normalize(self, item: dict[str, Any]) -> dict[str, Any]:
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


class DiffAddedLinesProvider:
    def build_added_lines_map(
        self,
        base_sha: str,
        head_sha: str,
        changed_files: list[str],
    ) -> dict[str, set[int]]:
        return build_added_lines_map(base_sha, head_sha, changed_files)


class DuplicateFilter:
    def _as_int(self, value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def _is_new_duplicate(
        self,
        duplicate: dict[str, Any],
        added_lines: dict[str, set[int]],
    ) -> bool:
        for side in ("first", "second"):
            file_meta = duplicate[side]
            file_name = str(file_meta.get("name", ""))
            start = self._as_int(file_meta.get("start"))
            end = self._as_int(file_meta.get("end"))
            if not file_name or start <= 0 or end <= 0:
                continue

            changed_line_set = added_lines.get(file_name, set())
            if not changed_line_set:
                continue

            for line_no in range(start, end + 1):
                if line_no in changed_line_set:
                    return True
        return False

    def filter_new_duplicates(
        self,
        duplicates: list[dict[str, Any]],
        base_sha: str,
        head_sha: str,
        changed_files: list[str],
    ) -> list[dict[str, Any]]:
        added_lines_map = build_added_lines_map(base_sha, head_sha, changed_files)
        if changed_files and not added_lines_map:
            return duplicates
        return [
            duplicate
            for duplicate in duplicates
            if self._is_new_duplicate(duplicate, added_lines_map)
        ]


class MarkdownRenderer:
    def render(
        self,
        duplicates: list[dict[str, Any]],
        warn_threshold: int,
        fail_threshold: int,
    ) -> str:
        count = len(duplicates)
        status_type = resolve_status(count, warn_threshold, fail_threshold)
        if status_type == CiStatus.fail:
            status = (
                f"❌ Wykryto **{count}** nowych duplikatów "
                f"(próg blokujący: {fail_threshold})."
            )
        elif status_type == CiStatus.warn:
            status = (
                f"⚠️ Wykryto **{count}** nowych duplikatów "
                f"(próg ostrzegawczy: {warn_threshold})."
            )
        else:
            status = "✅ Brak nowych duplikatów w zmienionych plikach."

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
                f"{idx}. `{first['name']}` ({line_range(first)}) "
                f"↔ `{second['name']}` ({line_range(second)})",
            )
            if dup["fragment"]:
                snippet = dup["fragment"][:400]
                lines.append("   ```python")
                lines.extend(f"   {line}" for line in snippet.splitlines())
                lines.append("   ```")

        return "\n".join(lines)


class GithubOutputWriter:
    def write(
        self,
        output_path: Path,
        duplicate_count: int,
        duplicate_status: str,
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("a", encoding="utf-8") as fh:
            fh.write(f"duplicate_count={duplicate_count}\n")
            fh.write(f"duplicate_status={duplicate_status}\n")


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


def read_json_file(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = build_ci_parser("Generate duplicate report for changed files in PR.")
    args = parser.parse_args()

    normalizer = DuplicateNormalizer()
    duplicate_filter = DuplicateFilter()
    markdown_renderer = MarkdownRenderer()

    report_path = Path(args.report_json)
    if not report_path.exists():
        duplicates: list[dict[str, Any]] = []
    else:
        payload = read_json_file(report_path)
        raw_duplicates = payload.get("duplicates") or payload.get("clones") or []
        duplicates = [normalizer.normalize(item) for item in raw_duplicates]

    changed_files = split_csv(args.changed_files)
    new_duplicates = duplicate_filter.filter_new_duplicates(
        duplicates,
        args.base_sha,
        args.head_sha,
        changed_files,
    )

    count = len(new_duplicates)
    markdown = markdown_renderer.render(
        new_duplicates,
        args.warn_threshold,
        args.fail_threshold,
    )
    write_text_file(Path(args.output_md), markdown)

    status = resolve_status(count, args.warn_threshold, args.fail_threshold)
    append_output_vars(
        Path(args.github_output),
        {
            "duplicate_count": count,
            "duplicate_status": status.value,
        },
    )

    return exit_code_for_status(status)


if __name__ == "__main__":
    raise SystemExit(main())
