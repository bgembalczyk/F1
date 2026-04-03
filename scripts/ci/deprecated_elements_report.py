from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
repo_root_str = str(REPO_ROOT)
if repo_root_str not in sys.path:
    sys.path.insert(0, repo_root_str)

from scrapers.cli import get_deprecated_elements_report


def _build_rows(today: date) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    rows: list[dict[str, str]] = []
    expired: list[dict[str, str]] = []

    for module_path, deprecated_since, replacement, remove_after in get_deprecated_elements_report():
        remove_date = date.fromisoformat(remove_after)
        status = "expired" if remove_date < today else "active"
        row = {
            "module": module_path,
            "deprecated_since": deprecated_since,
            "replacement": replacement,
            "remove_after": remove_after,
            "status": status,
        }
        rows.append(row)
        if status == "expired":
            expired.append(row)

    return rows, expired


def _render_markdown(rows: list[dict[str, str]], expired_count: int) -> str:
    lines = [
        "# Deprecated Elements Report",
        "",
        f"Total deprecated elements: **{len(rows)}**.",
        f"Expired elements: **{expired_count}**.",
        "",
        "| Module | Deprecated since | Replacement | Remove after | Status |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['module']}` | {row['deprecated_since']} | `{row['replacement']}` | "
            f"{row['remove_after']} | {row['status']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deprecated elements CI report.")
    parser.add_argument("--report-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    today = date.today()
    rows, expired = _build_rows(today)

    report_json = {
        "generated_at": today.isoformat(),
        "deprecated_count": len(rows),
        "expired_count": len(expired),
        "items": rows,
    }

    report_json_path = Path(args.report_json)
    report_json_path.parent.mkdir(parents=True, exist_ok=True)
    report_json_path.write_text(
        json.dumps(report_json, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    output_md_path = Path(args.output_md)
    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    output_md_path.write_text(
        _render_markdown(rows, len(expired)),
        encoding="utf-8",
    )

    if expired:
        print("Deprecated elements past due date:")
        for row in expired:
            print(f"- {row['module']} (remove_after={row['remove_after']})")
        return 1

    print(f"Deprecated elements report generated: {len(rows)} items, no expired entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
