from __future__ import annotations

import argparse
import ast
import re
import subprocess
from collections import Counter
from pathlib import PurePosixPath

ARCHITECTURE_PREFIXES: tuple[str, ...] = (
    "layers/",
    "scrapers/base/",
    "tests/architecture/",
)
ADR_PATTERN = re.compile(r"\bADR-\d{4}\b", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Wymaga referencji ADR-XXXX, gdy PR/commit zmienia ścieżki "
            "architektoniczne i zmiana nie jest wyłącznie kosmetyczna."
        )
    )
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--pr-title", default="")
    parser.add_argument("--pr-body", default="")
    return parser.parse_args()


def list_changed_files(base_sha: str, head_sha: str) -> list[str]:
    proc = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "--diff-filter=ACMR",
            base_sha,
            head_sha,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def is_architecture_path(path: str) -> bool:
    normalized = PurePosixPath(path).as_posix()
    return any(normalized.startswith(prefix) for prefix in ARCHITECTURE_PREFIXES)


IMPORT_LINE_PATTERN = re.compile(r"^(?:from\s+\S+\s+import\s+.+|import\s+.+)$")
DOCSTRING_LINE_PATTERN = re.compile(r'^[rubfRUBF]*("""|\'\'\')')


def classify_diff_line(content: str) -> str:
    stripped = content.strip()
    if not stripped:
        return "whitespace-only"
    if stripped.startswith("#"):
        return "comment-only"
    if DOCSTRING_LINE_PATTERN.match(stripped) or stripped.endswith(('"""', "'''")):
        return "docstring-only"
    if IMPORT_LINE_PATTERN.match(stripped):
        return "import-statement"
    return "code"


def _normalize_stmt_list(stmts: list[ast.stmt]) -> list[ast.stmt]:
    normalized: list[ast.stmt] = []
    import_block: list[ast.stmt] = []

    def flush_import_block() -> None:
        nonlocal import_block
        if not import_block:
            return
        import_block = sorted(import_block, key=lambda node: ast.dump(node, include_attributes=False))
        normalized.extend(import_block)
        import_block = []

    for stmt in stmts:
        normalized_stmt = _normalize_tree(stmt)
        if isinstance(normalized_stmt, (ast.Import, ast.ImportFrom)):
            import_block.append(normalized_stmt)
            continue
        flush_import_block()
        normalized.append(normalized_stmt)

    flush_import_block()
    return normalized


def _normalize_tree(node: ast.AST) -> ast.AST:
    for field_name, field_value in ast.iter_fields(node):
        if isinstance(field_value, list):
            if field_value and all(isinstance(item, ast.stmt) for item in field_value):
                statements = [item for item in field_value if isinstance(item, ast.stmt)]
                if statements and isinstance(
                    statements[0],
                    (ast.Expr,),
                ) and isinstance(getattr(statements[0], "value", None), ast.Constant):
                    first_value = getattr(statements[0], "value")
                    if isinstance(first_value.value, str):
                        statements = statements[1:]
                setattr(node, field_name, _normalize_stmt_list(statements))
            else:
                for item in field_value:
                    if isinstance(item, ast.AST):
                        _normalize_tree(item)
        elif isinstance(field_value, ast.AST):
            _normalize_tree(field_value)
    return node


def python_ast_semantically_changed(base_source: str, head_source: str) -> bool:
    try:
        base_tree = ast.parse(base_source)
        head_tree = ast.parse(head_source)
    except SyntaxError:
        return True

    normalized_base = _normalize_tree(base_tree)
    normalized_head = _normalize_tree(head_tree)

    return ast.dump(normalized_base, include_attributes=False) != ast.dump(
        normalized_head,
        include_attributes=False,
    )


def _git_show_file(sha: str, path: str) -> str | None:
    proc = subprocess.run(
        ["git", "show", f"{sha}:{path}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def has_non_cosmetic_changes_in_file(base_sha: str, head_sha: str, path: str) -> bool:
    proc = subprocess.run(
        ["git", "diff", "--unified=0", "--no-color", base_sha, head_sha, "--", path],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return True

    line_classifications: list[tuple[str, str]] = []
    for line in proc.stdout.splitlines():
        if line.startswith(("+++", "---", "@@")):
            continue
        if not line.startswith(("+", "-")):
            continue
        marker = line[:1]
        payload = line[1:]
        line_classifications.append((marker, classify_diff_line(payload)))

    substantive = [(marker, classification) for marker, classification in line_classifications if classification not in {"whitespace-only", "comment-only"}]
    if not substantive:
        return False

    if path.endswith(".py"):
        removed_imports = Counter(
            line[1:].strip()
            for line in proc.stdout.splitlines()
            if line.startswith("-") and classify_diff_line(line[1:]) == "import-statement"
        )
        added_imports = Counter(
            line[1:].strip()
            for line in proc.stdout.splitlines()
            if line.startswith("+") and classify_diff_line(line[1:]) == "import-statement"
        )
        only_import_lines = all(classification == "import-statement" for _, classification in substantive)
        if only_import_lines and removed_imports == added_imports:
            return False

        base_source = _git_show_file(base_sha, path)
        head_source = _git_show_file(head_sha, path)
        if base_source is not None and head_source is not None:
            if not python_ast_semantically_changed(base_source, head_source):
                return False

    return True


def has_non_cosmetic_changes(base_sha: str, head_sha: str, files: list[str]) -> bool:
    if not files:
        return False

    for path in files:
        if has_non_cosmetic_changes_in_file(base_sha, head_sha, path):
            return True

    return False


def collect_commit_messages(base_sha: str, head_sha: str) -> str:
    proc = subprocess.run(
        ["git", "log", "--format=%B", f"{base_sha}..{head_sha}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return ""
    return proc.stdout


def main() -> int:
    args = parse_args()

    changed_files = list_changed_files(args.base_sha, args.head_sha)
    architecture_files = [path for path in changed_files if is_architecture_path(path)]

    if not architecture_files:
        print("Brak zmian w ścieżkach architektonicznych; gate ADR pominięty.")
        return 0

    if not has_non_cosmetic_changes(args.base_sha, args.head_sha, architecture_files):
        print(
            "Wykryto wyłącznie zmiany kosmetyczne (formatowanie/komentarze) "
            "w ścieżkach architektonicznych; gate ADR pominięty."
        )
        return 0

    combined_text = "\n".join(
        [
            args.pr_title,
            args.pr_body,
            collect_commit_messages(args.base_sha, args.head_sha),
        ]
    )

    if ADR_PATTERN.search(combined_text):
        print("Referencja ADR-XXXX znaleziona. Gate ADR zaliczony.")
        return 0

    print("::error::Zmiany architektoniczne wymagają referencji ADR-XXXX w PR lub commit message.")
    print(f"::error::Dotknięte ścieżki: {', '.join(architecture_files)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
