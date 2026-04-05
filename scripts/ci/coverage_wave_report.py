from __future__ import annotations

import argparse
import ast
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

ROOT_PREFIX = str(Path(__file__).resolve().parents[2]) + "/"

WAVE1_MIN_MISS = 40
WAVE2_MIN_MISS = 20
WAVE2_MAX_MISS = 39
DEFAULT_TOP_LIMIT = 30

WAVE1 = "Fala 1"
WAVE2 = "Fala 2"
WAVE3 = "Fala 3"
WAVE4 = "Fala 4"


@dataclass(frozen=True)
class FileMiss:
    path: str
    statements: int
    executed: int
    miss: int


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a coverage wave report and top remaining misses from "
            ".coverage SQLite data."
        ),
    )
    parser.add_argument("--coverage-db", default=".coverage")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--top", type=int, default=DEFAULT_TOP_LIMIT)
    parser.add_argument(
        "--json-out",
        default="artifacts/coverage_top_remaining_misses.json",
    )
    parser.add_argument(
        "--md-out",
        default="artifacts/coverage_top_remaining_misses.md",
    )
    parser.add_argument("--backlog-out", default="docs/COVERAGE_WAVE_BACKLOG.md")
    return parser.parse_args()


def _normalize_path(raw_path: str) -> str:
    if raw_path.startswith(ROOT_PREFIX):
        return raw_path.removeprefix(ROOT_PREFIX)
    return raw_path


def _load_executed_lines(coverage_db: Path) -> dict[str, set[int]]:
    conn = sqlite3.connect(coverage_db)
    try:
        rows = conn.execute(
            """
            SELECT f.path, lb.numbits
            FROM file AS f
            JOIN line_bits AS lb ON f.id = lb.file_id
            """,
        )
        per_file: dict[str, set[int]] = {}
        for raw_path, numbits in rows:
            norm = _normalize_path(raw_path)
            line_set = per_file.setdefault(norm, set())
            for index, byte in enumerate(numbits):
                for bit in range(8):
                    if byte & (1 << bit):
                        line_set.add(index * 8 + bit + 1)
        return per_file
    finally:
        conn.close()


def _statement_lines(path: Path) -> set[int]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    statements: set[int] = set()
    for node in ast.walk(tree):
        lineno = getattr(node, "lineno", None)
        if lineno is None:
            continue
        if isinstance(node, ast.stmt):
            statements.add(int(lineno))
    return statements


def _collect_misses(repo_root: Path, executed: dict[str, set[int]]) -> list[FileMiss]:
    rows: list[FileMiss] = []
    for rel_path, executed_lines in executed.items():
        if not rel_path.endswith(".py"):
            continue
        if rel_path.startswith("tests/"):
            continue
        full_path = repo_root / rel_path
        if not full_path.exists():
            continue
        stmt_lines = _statement_lines(full_path)
        if not stmt_lines:
            continue
        executed_stmt_count = len(stmt_lines & executed_lines)
        miss = len(stmt_lines) - executed_stmt_count
        rows.append(
            FileMiss(
                path=rel_path,
                statements=len(stmt_lines),
                executed=executed_stmt_count,
                miss=miss,
            ),
        )
    rows.sort(key=lambda row: (-row.miss, row.path))
    return rows


def _wave_for_path(path: str, miss: int) -> str:
    low = path.lower()
    if miss >= WAVE1_MIN_MISS and (
        "parser" in low or "helper" in low or low.startswith("scripts/ci/")
    ):
        return WAVE1
    if WAVE2_MIN_MISS <= miss <= WAVE2_MAX_MISS and (
        "domain" in low or "service" in low or "services" in low
    ):
        return WAVE2
    if miss >= 1:
        return WAVE3
    return WAVE4


def _to_dict(file_miss: FileMiss) -> dict[str, object]:
    return {
        "path": file_miss.path,
        "statements": file_miss.statements,
        "executed": file_miss.executed,
        "miss": file_miss.miss,
        "coverage": round(100 * file_miss.executed / file_miss.statements, 2),
        "wave": _wave_for_path(file_miss.path, file_miss.miss),
    }


def _render_top_md(top: list[dict[str, object]]) -> str:
    lines = [
        "# Top remaining misses",
        "",
        "| # | File | Miss | Coverage | Wave |",
        "|---:|---|---:|---:|---|",
    ]
    for idx, item in enumerate(top, start=1):
        lines.append(
            "| "
            f"{idx} | `{item['path']}` | {item['miss']} | "
            f"{item['coverage']}% | {item['wave']} |",
        )
    lines.append("")
    return "\n".join(lines)


def _render_backlog_md(top: list[dict[str, object]]) -> str:
    grouped: dict[str, list[dict[str, object]]] = {
        WAVE1: [],
        WAVE2: [],
        WAVE3: [],
        WAVE4: [],
    }
    for item in top:
        grouped[item["wave"]].append(item)

    lines = [
        "# Coverage backlog (aktualizacja automatyczna)",
        "",
        "## Cele fal",
        (
            "- Fala 1 (najwyższy ROI): parsery/helpers + scripts CI z "
            f"`miss >= {WAVE1_MIN_MISS}`; cel: +6-7 pp."
        ),
        (
            "- Fala 2: moduły domenowe i services z `miss "
            f"{WAVE2_MIN_MISS}-{WAVE2_MAX_MISS}`; cel: +3-4 pp."
        ),
        (
            "- Fala 3: domknięcie wyjątków/fallbacków i niskich plików "
            "pojedynczych; cel: +2-3 pp."
        ),
        "- Fala 4: polerka do 99% - pojedyncze linie i granice warunków; cel: +1-2 pp.",
        "",
    ]
    for wave, items in grouped.items():
        lines.append(f"## {wave}")
        if not items:
            lines.append("- Brak plików w top N.")
        else:
            lines.extend(
                [
                    (
                        f"- [ ] `{item['path']}` - miss: {item['miss']}, "
                        f"coverage: {item['coverage']}%"
                    )
                    for item in items
                ],
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = _parse_args()
    repo_root = Path(args.repo_root).resolve()
    executed = _load_executed_lines(Path(args.coverage_db))
    misses = _collect_misses(repo_root, executed)
    top_rows = [_to_dict(row) for row in misses[: args.top] if row.miss > 0]

    json_out = Path(args.json_out)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(
        json.dumps(top_rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    md_out = Path(args.md_out)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.write_text(_render_top_md(top_rows), encoding="utf-8")

    backlog_out = Path(args.backlog_out)
    backlog_out.parent.mkdir(parents=True, exist_ok=True)
    backlog_out.write_text(_render_backlog_md(top_rows), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
