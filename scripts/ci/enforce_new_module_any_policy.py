#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROLLOUT_PREFIXES = (
    "layers/",
    "validation/",
    "infrastructure/http_client/",
)

# Tymczasowa lista wyjątków (legacy debt) — utrzymywana jawnie podczas rolloutu.
ANY_EXCEPTION_MODULES = {
    "layers/application.py",
    "layers/one/executor.py",
    "layers/orchestration/runners/function_export.py",
    "layers/orchestration/runners/grand_prix.py",
    "layers/seed/data_classes.py",
    "layers/seed/helpers.py",
    "layers/seed/registry/constants.py",
    "layers/seed/registry/entries.py",
    "layers/seed/registry/helpers.py",
    "layers/zero/executor.py",
    "layers/zero/merge.py",
    "validation/composite_validator.py",
    "validation/record_factory_validator.py",
    "validation/rules.py",
    "validation/schema_engine.py",
    "validation/schema_rules.py",
    "validation/schemas.py",
    "validation/validator_base.py",
    "infrastructure/http_client/clients/base.py",
    "infrastructure/http_client/clients/urllib_http.py",
    "infrastructure/http_client/components/request_executor.py",
    "infrastructure/http_client/interfaces/http_client_protocol.py",
    "infrastructure/http_client/policies/default_retry.py",
    "infrastructure/http_client/policies/retry.py",
    "infrastructure/http_client/requests_shim/http_error.py",
    "infrastructure/http_client/requests_shim/session.py",
}

JUSTIFICATION_MARKER = "ANY-JUSTIFIED:"
ANY_PATTERN = re.compile(r"\bAny\b")


def _git(*args: str) -> str:
    res = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return res.stdout


def _new_python_files(base_sha: str, head_sha: str) -> list[str]:
    output = _git("diff", "--name-only", "--diff-filter=A", base_sha, head_sha, "--", "*.py")
    files = [line.strip() for line in output.splitlines() if line.strip()]
    return [
        path
        for path in files
        if path.startswith(ROLLOUT_PREFIXES) and path not in ANY_EXCEPTION_MODULES
    ]


def _scan_file(path: Path) -> list[str]:
    violations: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines, start=1):
        if not ANY_PATTERN.search(line):
            continue
        if JUSTIFICATION_MARKER in line:
            continue
        if idx > 1 and JUSTIFICATION_MARKER in lines[idx - 2]:
            continue
        violations.append(f"{path}:{idx}: użyto 'Any' bez uzasadnienia ({JUSTIFICATION_MARKER})")
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Blokuje nowe moduły z Any bez uzasadnienia w obszarze rolloutu typingu."
    )
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    args = parser.parse_args()

    new_files = _new_python_files(args.base_sha, args.head_sha)
    if not new_files:
        print("Brak nowych modułów Python w scope rolloutu typingu.")
        return 0

    violations: list[str] = []
    for rel_path in new_files:
        violations.extend(_scan_file(Path(rel_path)))

    if violations:
        print("Znaleziono naruszenia polityki Any dla nowych modułów:")
        for issue in violations:
            print(f" - {issue}")
        return 1

    print("Polityka Any dla nowych modułów: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
