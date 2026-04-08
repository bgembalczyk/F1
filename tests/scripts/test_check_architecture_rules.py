from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import check_architecture_rules


def rules_stub() -> SimpleNamespace:
    def _infer_layer(path: Path, *, domain: str | None = None) -> str:
        _ = domain
        return "sections" if "sections" in path.parts else "app"

    return SimpleNamespace(
        LAYERS={"sections", "app"},
        DOMAINS=("drivers", "seasons"),
        ENTRYPOINT_DOMAINS=("drivers",),
        REQUIRED_LAYERS_BY_DOMAIN={"drivers": ("sections", "app")},
        FORBIDDEN_IMPORTS_BY_LAYER={"sections": ("app",), "app": ()},
        infer_layer=_infer_layer,
        resolve_import_targets=lambda _path: ["scrapers.drivers.app.shared"],
        collect_cross_domain_import_violations=lambda _path, _domain: [
            "scrapers.seasons.app",
        ],
        collect_single_scraper_import_violations=lambda _path, _domain: [
            "scrapers.drivers.single_scraper",
        ],
    )


def test_checks_cover_required_layout_boundaries_and_cross_domain(
    tmp_path: Path,
) -> None:
    root = tmp_path / "scrapers"
    domain = root / "drivers"
    (domain / "sections").mkdir(parents=True)
    (domain / "app").mkdir()
    (domain / "sections" / "feature.py").write_text("pass\n", encoding="utf-8")
    (domain / "app" / "feature.py").write_text("pass\n", encoding="utf-8")

    rules = rules_stub()

    required_errors = check_architecture_rules.check_required_layout(
        root,
        ("drivers",),
        rules,
    )
    boundary_errors = check_architecture_rules.check_layer_boundaries(
        root,
        ("drivers",),
        rules,
    )
    _check_ss = check_architecture_rules.check_sections_single_scraper_boundary
    section_errors = _check_ss(
        root,
        ("drivers",),
        rules,
    )
    cross_errors = check_architecture_rules.check_cross_domain_imports(
        root,
        ("drivers",),
        rules,
    )

    assert any("Missing facade entrypoint" in err for err in required_errors)
    assert any("Layer boundary violation" in err for err in boundary_errors)
    assert any("Forbidden import direction" in err for err in section_errors)
    assert any("Cross-domain import" in err for err in cross_errors)


def test_detect_relevant_domains_accepts_only_scrapers_python_paths() -> None:
    detected = check_architecture_rules.detect_relevant_domains(
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
    rules = rules_stub()
    monkeypatch.setattr(
        check_architecture_rules,
        "_load_architecture_rules",
        lambda: rules,
    )
    monkeypatch.setattr(
        check_architecture_rules,
        "_detect_relevant_domains",
        lambda *_args, **_kwargs: set(),
    )

    monkeypatch.setattr(
        check_architecture_rules,
        "_check_required_layout",
        lambda *_a, **_k: ["broken"],
    )
    monkeypatch.setattr(
        check_architecture_rules,
        "_check_layer_boundaries",
        lambda *_a, **_k: [],
    )
    monkeypatch.setattr(
        check_architecture_rules,
        "_check_sections_single_scraper_boundary",
        lambda *_a, **_k: [],
    )
    monkeypatch.setattr(
        check_architecture_rules,
        "_check_cross_domain_imports",
        lambda *_a, **_k: [],
    )

    assert check_architecture_rules.main() == 1
    output = capsys.readouterr().out
    assert "Architecture rules check failed" in output
    assert "- broken" in output

    monkeypatch.setattr(
        check_architecture_rules,
        "_check_required_layout",
        lambda *_a, **_k: [],
    )
    assert check_architecture_rules.main() == 0
    assert "Architecture rules check passed." in capsys.readouterr().out


def test_cli_invalid_argument_reports_stderr(
    capsys: pytest.CaptureFixture[str],
) -> None:
    old_argv = sys.argv
    try:
        sys.argv = ["check_architecture_rules.py", "--bad-flag"]
        with pytest.raises(SystemExit) as exc:
            check_architecture_rules.main()
        assert exc.value.code == 2  # noqa: PLR2004
    finally:
        sys.argv = old_argv

    err = capsys.readouterr().err
    assert "usage:" in err
    assert "unrecognized arguments" in err
