from __future__ import annotations

from pathlib import Path

from scripts.ci import enforce_record_factory_contracts as check


def test_detects_forbidden_legacy_imports_and_create_methods(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    repo = tmp_path / "repo"
    (repo / "models" / "records" / "factories").mkdir(parents=True)
    (repo / "models" / "records").mkdir(parents=True, exist_ok=True)

    (repo / "models" / "records" / "factories" / "bad.py").write_text(
        "from models.records.factories.compat import create_compat\n"
        "\n"
        "class BadFactory:\n"
        "    def create(self, payload):\n"
        "        return payload\n",
        encoding="utf-8",
    )
    (repo / "models" / "records" / "consumer.py").write_text(
        "from models.records.base_factory import RecordBuilderProtocol\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(repo)

    exit_code = check.main()

    out = capsys.readouterr().out
    assert exit_code == 1
    assert "[enforce_record_factory_contracts] ERROR" in out
    assert "forbidden import from 'models.records.factories.compat'" in out
    assert "forbidden 'create(...)' method" in out
    assert "forbidden symbol 'RecordBuilderProtocol'" in out


def test_accepts_canonical_record_builder_contract(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    repo = tmp_path / "repo"
    (repo / "models" / "records" / "factories").mkdir(parents=True)
    (repo / "models" / "records").mkdir(parents=True, exist_ok=True)

    (repo / "models" / "records" / "factories" / "ok.py").write_text(
        "class OkFactory:\n"
        "    def build(self, record):\n"
        "        return dict(record)\n",
        encoding="utf-8",
    )
    (repo / "models" / "records" / "consumer.py").write_text(
        "from models.records.factories.protocol import RecordBuilderProtocol\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(repo)

    exit_code = check.main()

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "[enforce_record_factory_contracts] OK" in out
