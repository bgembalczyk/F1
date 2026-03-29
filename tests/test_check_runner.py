from __future__ import annotations

from pathlib import Path

from scripts.lib.check_runner import parse_target_paths


def test_parse_target_paths_uses_defaults_when_flag_missing() -> None:
    defaults = [Path("default-dir")]

    paths, remaining = parse_target_paths([], default_paths=defaults)

    assert paths == defaults
    assert remaining == []


def test_parse_target_paths_supports_explicit_empty_target_list() -> None:
    paths, remaining = parse_target_paths(
        ["--paths"],
        default_paths=[Path("unused")],
    )

    assert paths == []
    assert remaining == []


def test_parse_target_paths_resolves_explicit_targets_against_repo_root() -> None:
    repo_root = Path("/repo")

    paths, remaining = parse_target_paths(
        ["--paths", "scrapers", "layers/a.py", "--adr-reference-text", "ADR-0001"],
        default_paths=[Path("unused")],
        repo_root=repo_root,
    )

    assert paths == [repo_root / "scrapers", repo_root / "layers/a.py"]
    assert remaining == ["--adr-reference-text", "ADR-0001"]
