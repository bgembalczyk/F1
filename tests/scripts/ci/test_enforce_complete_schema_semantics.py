from __future__ import annotations

from pathlib import Path

from scripts.ci import enforce_complete_schema_semantics as gate


def test_run_reports_complete_schema_with_sparse_required_fields(tmp_path: Path) -> None:
    file_path = tmp_path / "record.py"
    file_path.write_text(
        """
from validation.schemas import RecordSchema

CIRCUIT_COMPLETE_SCHEMA = RecordSchema(required=("url",))
""".strip(),
        encoding="utf-8",
    )

    issues = gate.run(tmp_path)

    assert len(issues) == 1
    assert "CIRCUIT_COMPLETE_SCHEMA" in issues[0]


def test_run_accepts_complete_schema_with_domain_required_fields(tmp_path: Path) -> None:
    file_path = tmp_path / "record.py"
    file_path.write_text(
        """
from models.records.record_definition import RecordDefinition

TEAM_FULL_DEFINITION = RecordDefinition(
    name="team_full",
    required=("name", "country", "titles"),
)
""".strip(),
        encoding="utf-8",
    )

    issues = gate.run(tmp_path)

    assert issues == []


def test_main_returns_zero_when_no_violations(tmp_path: Path, monkeypatch) -> None:
    file_path = tmp_path / "record.py"
    file_path.write_text(
        """
from validation.schemas import RecordSchema

SEASON_SCHEMA = RecordSchema(required=("year", "url"))
""".strip(),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        gate,
        "parse_args",
        lambda: type("Args", (), {"root": str(tmp_path)})(),
    )

    assert gate.main() == 0
