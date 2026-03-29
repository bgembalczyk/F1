#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

PY_MODULE_DIRS=(scrapers layers models validation infrastructure)
WARN_THRESHOLD="${NEW_DUPLICATES_WARN_THRESHOLD:-1}"
FAIL_THRESHOLD="${NEW_DUPLICATES_FAIL_THRESHOLD:-3}"

log() {
  printf '\n[pre-commit] %s\n' "$1"
}

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    printf '[pre-commit] Brak wymaganego polecenia: %s\n' "$cmd" >&2
    exit 1
  fi
}

run_python_cmd() {
  if command -v python >/dev/null 2>&1; then
    python "$@"
  elif command -v python3 >/dev/null 2>&1; then
    python3 "$@"
  else
    printf '[pre-commit] Brak interpretera python/python3\n' >&2
    exit 1
  fi
}

collect_staged_python_files() {
  git diff --cached --name-only --diff-filter=ACMR -- '*.py' || true
}

run_duplicate_gate() {
  log "Skan duplikatów (jscpd) dla staged *.py"

  if ! command -v npx >/dev/null 2>&1; then
    printf '[pre-commit] Brak npx (Node.js). Zainstaluj Node.js 20+ aby uruchomić jscpd.\n' >&2
    exit 1
  fi

  mapfile -t staged_python_files < <(collect_staged_python_files)
  if [[ ${#staged_python_files[@]} -eq 0 ]]; then
    printf '[pre-commit] Brak staged plików Python - pomijam jscpd.\n'
    return
  fi

  local report_dir=".jscpd-report"
  local report_json="$report_dir/jscpd-report.json"
  mkdir -p "$report_dir"

  npx --yes jscpd \
    --pattern "**/*.py" \
    --min-lines 5 \
    --min-tokens 50 \
    --threshold 100 \
    --reporters json \
    --output "$report_dir" \
    "${staged_python_files[@]}"

  run_python_cmd - <<'PY'
import json
from pathlib import Path

warn_threshold = int(__import__('os').environ.get('NEW_DUPLICATES_WARN_THRESHOLD', '1'))
fail_threshold = int(__import__('os').environ.get('NEW_DUPLICATES_FAIL_THRESHOLD', '3'))
report_path = Path('.jscpd-report/jscpd-report.json')
if not report_path.exists():
    dup_count = 0
else:
    payload = json.loads(report_path.read_text(encoding='utf-8'))
    dup_count = len(payload.get('duplicates') or payload.get('clones') or [])

print(f"[pre-commit] Nowe duplikaty: {dup_count}")
if dup_count >= fail_threshold:
    raise SystemExit(f"[pre-commit] FAIL: przekroczono próg blokujący ({fail_threshold}).")
if dup_count >= warn_threshold:
    print(f"[pre-commit] WARN: przekroczono próg ostrzegawczy ({warn_threshold}).")
PY
}

log "Sprawdzenie dependency tooling"
require_cmd radon
require_cmd xenon
require_cmd pylint
require_cmd lint-imports
require_cmd mypy
require_cmd pytest

log "Complexity warning threshold (radon)"
radon cc "${PY_MODULE_DIRS[@]}" --show-complexity --min B || true

log "Complexity error threshold (xenon)"
xenon "${PY_MODULE_DIRS[@]}" --max-absolute C --max-modules C --max-average B

log "Duplicate code / oversized units gate (pylint)"
pylint "${PY_MODULE_DIRS[@]}" --rcfile=.pylintrc

run_duplicate_gate

log "Architectural import rules (import-linter)"
lint-imports --config importlinter.ini

log "Strict typing regression gate (mypy)"
mypy --config-file mypy.ini

log "Domain contracts gate (pytest)"
pytest -q tests/test_domain_role_contracts.py tests/test_domain_role_contracts_ci_meta.py

log "Known module typos gate"
run_python_cmd scripts/check_known_module_typos.py

log "Architecture tests gate"
pytest -q \
  tests/test_architecture_import_rules.py \
  tests/test_architecture_duplicate_blocks.py \
  tests/test_base_contracts.py \
  tests/test_domain_entrypoints_contract.py \
  tests/test_section_architecture_boundaries.py

log "Wszystkie hooki pre-commit zakończone sukcesem."
