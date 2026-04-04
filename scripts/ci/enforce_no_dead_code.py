from __future__ import annotations

import argparse
import subprocess
import sys


DEFAULT_TARGETS = ["layers", "models", "scrapers", "validation", "infrastructure", "complete_extractor", "config"]
DEFAULT_EXCLUDES = ["*/tests/*", "*/test_*", "*/__init__.py", "*/scripts/*", "*/data/*"]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fail CI when dead code is detected by vulture.")
    parser.add_argument("paths", nargs="*", default=DEFAULT_TARGETS)
    parser.add_argument("--min-confidence", type=int, default=90)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    exclude_arg = ",".join(DEFAULT_EXCLUDES)
    command = [
        sys.executable,
        "-m",
        "vulture",
        *args.paths,
        "--min-confidence",
        str(args.min_confidence),
        "--exclude",
        exclude_arg,
    ]
    result = subprocess.run(command, check=False)
    if result.returncode == 0:
        print("Dead code gate: OK")
        return 0

    print("::error::Potential dead code detected. Remove unused production symbols/files and related tests.")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
