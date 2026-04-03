# ruff: noqa: S603
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from scripts.ci.git_diff import build_added_lines_map
from scripts.ci.io_utils import append_output_vars
from scripts.ci.io_utils import read_json_file
from scripts.ci.io_utils import write_text_file
from scripts.ci.reporting import CiStatus
from scripts.ci.reporting import build_ci_parser
from scripts.ci.reporting import exit_code_for_status
from scripts.ci.reporting import resolve_status
from scripts.ci.reporting import split_csv


@dataclass(frozen=True)
class DuplicateFileMeta:
    name: str
    start: int
    end: int


@dataclass(frozen=True)
class DuplicateRecord:
    first: DuplicateFileMeta
    second: DuplicateFileMeta
    fragment: str


class DuplicateNormalizer:
    @staticmethod
    def _as_mapping(value: object) -> Mapping[str, object]:
        if isinstance(value, Mapping):
            return value
        return {}

    @staticmethod
    def _as_int(value: object) -> int:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return 0
        return 0

    def _normalize_file_meta(self, payload: Mapping[str, object]) -> DuplicateFileMeta:
        name_obj = payload.get("name") or payload.get("path") or "<unknown>"
        return DuplicateFileMeta(
            name=str(name_obj),
            start=self._as_int(payload.get("start") or payload.get("startLoc")),
            end=self._as_int(payload.get("end") or payload.get("endLoc")),
        )

    def normalize(self, item: Mapping[str, object]) -> DuplicateRecord:
        first = self._normalize_file_meta(self._as_mapping(item.get("firstFile")))
        second = self._normalize_file_meta(self._as_mapping(item.get("secondFile")))
        fragment = item.get("fragment") or item.get("codefragment") or ""
        return DuplicateRecord(
            first=first,
            second=second,
            fragment=str(fragment).strip(),
        )


class DuplicateFilter:
    def _is_new_duplicate(
        self,
        duplicate: DuplicateRecord,
        added_lines: dict[str, set[int]],
    ) -> bool:
        for file_meta in (duplicate.first, duplicate.second):
            if not file_meta.name or file_meta.start <= 0 or file_meta.end <= 0:
                continue

            changed_line_set = added_lines.get(file_meta.name, set())
            if not changed_line_set:
                continue

            for line_no in range(file_meta.start, file_meta.end + 1):
                if line_no in changed_line_set:
                    return True
        return False

    def filter_new_duplicates(
        self,
        duplicates: list[DuplicateRecord],
        base_sha: str,
        head_sha: str,
        changed_files: list[str],
    ) -> list[DuplicateRecord]:
        added_lines_map = build_added_lines_map(base_sha, head_sha, changed_files)
        if changed_files and not added_lines_map:
            return duplicates
        return [
            duplicate
            for duplicate in duplicates
            if self._is_new_duplicate(duplicate, added_lines_map)
        ]


class MarkdownRenderer:
    @staticmethod
    def _line_range(meta: DuplicateFileMeta) -> str:
        if meta.start and meta.end:
            return f"L{meta.start}-L{meta.end}"
        return "line ?"

    def render(
        self,
        duplicates: list[DuplicateRecord],
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
            lines.append(
                f"{idx}. `{dup.first.name}` ({self._line_range(dup.first)}) "
                f"↔ `{dup.second.name}` ({self._line_range(dup.second)})",
            )
            if dup.fragment:
                snippet = dup.fragment[:400]
                lines.append("   ```python")
                lines.extend(f"   {line}" for line in snippet.splitlines())
                lines.append("   ```")

        return "\n".join(lines)


def main() -> int:
    parser = build_ci_parser("Generate duplicate report for changed files in PR.")
    args = parser.parse_args()

    normalizer = DuplicateNormalizer()
    duplicate_filter = DuplicateFilter()
    markdown_renderer = MarkdownRenderer()

    payload = read_json_file(Path(args.report_json))
    raw_duplicates = payload.get("duplicates") or payload.get("clones") or []
    duplicates = [
        normalizer.normalize(item)
        for item in raw_duplicates
        if isinstance(item, Mapping)
    ]

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
