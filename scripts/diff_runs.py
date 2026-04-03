#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path
from typing import Any


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _canonicalize(path: Path) -> str:
    if path.suffix == ".json":
        return _canonical_json(json.loads(_read_text(path)))
    if path.suffix == ".jsonl":
        rows = [json.loads(line) for line in _read_text(path).splitlines() if line.strip()]
        return _canonical_json(rows)
    return _read_text(path)


def _collect_files(base: Path) -> dict[Path, Path]:
    if base.is_file():
        return {Path(base.name): base}
    return {
        file_path.relative_to(base): file_path
        for file_path in sorted(path for path in base.rglob("*") if path.is_file())
    }


def diff_runs(left: Path, right: Path) -> int:
    left_files = _collect_files(left)
    right_files = _collect_files(right)
    all_rel_paths = sorted(set(left_files) | set(right_files))

    changed = False
    for rel_path in all_rel_paths:
        left_path = left_files.get(rel_path)
        right_path = right_files.get(rel_path)
        if left_path is None:
            print(f"ONLY_RIGHT {rel_path}")
            changed = True
            continue
        if right_path is None:
            print(f"ONLY_LEFT {rel_path}")
            changed = True
            continue

        left_text = _canonicalize(left_path)
        right_text = _canonicalize(right_path)
        if left_text == right_text:
            continue
        changed = True
        print(f"DIFF {rel_path}")
        diff = difflib.unified_diff(
            left_text.splitlines(),
            right_text.splitlines(),
            fromfile=str(left_path),
            tofile=str(right_path),
            lineterm="",
        )
        for line in diff:
            print(line)
    return 1 if changed else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Diff artifacts from two pipeline runs.")
    parser.add_argument("left", type=Path, help="Left run artifact directory or file.")
    parser.add_argument("right", type=Path, help="Right run artifact directory or file.")
    args = parser.parse_args()
    raise SystemExit(diff_runs(args.left, args.right))


if __name__ == "__main__":
    main()
