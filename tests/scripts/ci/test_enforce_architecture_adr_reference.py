from __future__ import annotations

import os
import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest

from scripts.ci import enforce_architecture_adr_reference as gate


def test_parse_args_accepts_and_rejects_arguments() -> None:
    args = gate.parse_args(["--base-sha", "a", "--head-sha", "b", "--pr-title", "x"])
    assert args.base_sha == "a"
    assert args.head_sha == "b"


def test_resolve_sha_pair_uses_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_SHA", "head-env")
    monkeypatch.setenv("GITHUB_BASE_SHA", "base-env")

    assert gate.resolve_sha_pair("", "") == ("base-env", "head-env")


def test_has_non_cosmetic_changes_handles_all_branches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert gate.has_non_cosmetic_changes("a", "b", []) is False

    class BadDiff:
        returncode = 1
        stdout = ""

    monkeypatch.setattr(gate, "get_unified_diff", lambda *_a, **_k: BadDiff())
    assert gate.has_non_cosmetic_changes("a", "b", ["layers/pipeline.py"])

    class EmptyDiff:
        returncode = 0
        stdout = ""

    monkeypatch.setattr(gate, "get_unified_diff", lambda *_a, **_k: EmptyDiff())
    assert not gate.has_non_cosmetic_changes("a", "b", ["layers/pipeline.py"])


def test_has_adr_reference_uses_custom_checker_when_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Policy:
        adr_pattern = gate.DEFAULT_ADR_ENFORCEMENT_POLICY.adr_pattern

        @staticmethod
        def has_adr_reference(_text: str) -> bool:
            return True

    monkeypatch.setattr(gate, "DEFAULT_ADR_ENFORCEMENT_POLICY", Policy())

    assert gate._has_adr_reference("without marker")


def test_main_outputs_error_when_reference_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "argv", ["prog", "--base-sha", "a", "--head-sha", "b"])
    monkeypatch.setattr(
        gate,
        "list_changed_files",
        lambda *_a, **_k: ["layers/pipeline.py"],
    )
    monkeypatch.setattr(gate, "has_non_cosmetic_changes", lambda *_a, **_k: True)
    monkeypatch.setattr(gate, "collect_commit_messages", lambda *_a, **_k: "")

    assert gate.main() == 1
    out = capsys.readouterr().out
    assert "::error::Zmiany architektoniczne" in out
    assert "Dotknięte ścieżki" in out


def test_cli_invalid_argument_prints_stderr() -> None:
    proc = subprocess.run(  # noqa: S603 - controlled test command
        [
            sys.executable,
            "-m",
            "scripts.ci.enforce_architecture_adr_reference",
            "--bad",
        ],
        capture_output=True,
        text=True,
        check=False,
        env=dict(os.environ),
    )

    assert proc.returncode == 2  # noqa: PLR2004
    assert "usage:" in proc.stderr
    assert "unrecognized arguments" in proc.stderr
