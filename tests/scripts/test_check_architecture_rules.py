from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import check_architecture_rules


def _rules_stub() -> SimpleNamespace:
    return SimpleNamespace(
        LAYERS={"sections", "app"},
        DOMAINS=("drivers", "seasons"),
        ENTRYPOINT_DOMAINS=("drivers",),
        REQUIRED_LAYERS_BY_DOMAIN={"drivers": ("sections", "app")},
        FORBIDDEN_IMPORTS_BY_LAYER={"sections": ("app",), "app": tuple()},
        infer_layer=lambda path, domain=None: "sections" if "sections" in path.parts else "app",
        resolve_import_targets=lambda _path: ["scrapers.drivers.app.shared"],
        collect_cross_domain_import_violations=lambda _path, _domain: ["scrapers.seasons.app"],
        collect_single_scraper_import_violations=lambda _path, _domain: ["scrapers.drivers.single_scraper"],
    )


def test_checks_cover_required_layout_boundaries_and_cross_domain(tmp_path: Path) -> None:
    root = tmp_path / "scrapers"
    domain = root / "drivers"
    (domain / "sections").mkdir(parents=True)
    (domain / "app").mkdir()
    (domain / "sections" / "feature.py").write_text("pass\n", encoding="utf-8")
    (domain / "app" / "feature.py").write_text("pass\n", encoding="utf-8")

    rules = _rules_stub()

    required_errors = check_architecture_rules._check_required_layout(  # noqa: SLF001
        root,
        ("drivers",),
        rules,
    )
    boundary_errors = check_architecture_rules._check_layer_boundaries(  # noqa: SLF001
        root,
        ("drivers",),
        rules,
    )
    section_errors = check_architecture_rules._check_sections_single_scraper_boundary(  # noqa: SLF001
        root,
        ("drivers",),
        rules,
    )
    cross_errors = check_architecture_rules._check_cross_domain_imports(  # noqa: SLF001
        root,
        ("drivers",),
        rules,
    )

    assert any("Missing facade entrypoint" in err for err in required_errors)
    assert any("Layer boundary violation" in err for err in boundary_errors)
    assert any("Forbidden import direction" in err for err in section_errors)
    assert any("Cross-domain import" in err for err in cross_errors)


def test_detect_relevant_domains_accepts_only_scrapers_python_paths() -> None:
    detected = check_architecture_rules._detect_relevant_domains(  # noqa: SLF001
        [
            Path("scrapers/drivers/entrypoint.py"),
            Path("scrapers/unknown/file.py"),
            Path("docs/file.md"),
        ],
        domains=("drivers", "seasons"),
    )

    assert detected == {"drivers"}


def test_main_returns_failure_and_success_with_expected_stdout(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "argv", ["check_architecture_rules.py"])
    rules = _rules_stub()
    monkeypatch.setattr(check_architecture_rules, "_load_architecture_rules", lambda: rules)
    monkeypatch.setattr(check_architecture_rules, "_detect_relevant_domains", lambda *_args, **_kwargs: set())

    monkeypatch.setattr(check_architecture_rules, "_check_required_layout", lambda *_a, **_k: ["broken"])
    monkeypatch.setattr(check_architecture_rules, "_check_layer_boundaries", lambda *_a, **_k: [])
    monkeypatch.setattr(check_architecture_rules, "_check_sections_single_scraper_boundary", lambda *_a, **_k: [])
    monkeypatch.setattr(check_architecture_rules, "_check_cross_domain_imports", lambda *_a, **_k: [])

    assert check_architecture_rules.main() == 1
    output = capsys.readouterr().out
    assert "Architecture rules check failed" in output
    assert "- broken" in output

    monkeypatch.setattr(check_architecture_rules, "_check_required_layout", lambda *_a, **_k: [])
    assert check_architecture_rules.main() == 0
    assert "Architecture rules check passed." in capsys.readouterr().out


def test_cli_invalid_argument_reports_stderr() -> None:
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "check_architecture_rules.py"

    proc = subprocess.run(
        [sys.executable, str(script_path), "--bad-flag"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 2
    assert "usage:" in proc.stderr
    assert "unrecognized arguments" in proc.stderr
