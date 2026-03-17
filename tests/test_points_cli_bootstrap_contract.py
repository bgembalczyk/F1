from __future__ import annotations

from pathlib import Path

POINTS_PACKAGE_DIR = Path("scrapers/points")
ALLOWED_BOOTSTRAP_TOKENS = (
    "build_cli_main(",
    "run_cli_entrypoint(",
)
DISALLOWED_MANUAL_TOKENS = (
    "argparse.ArgumentParser(",
    'Path("../../data/wiki")',
    'Path("../../data/debug")',
    "RunConfig(",
)


def _module_sources_with_main_block() -> list[tuple[str, str]]:
    modules: list[tuple[str, str]] = []
    for file_path in sorted(POINTS_PACKAGE_DIR.glob("*.py")):
        source = file_path.read_text(encoding="utf-8")
        if 'if __name__ == "__main__":' in source:
            modules.append((str(file_path), source))
    return modules


def test_points_cli_modules_use_single_bootstrap_mechanism() -> None:
    modules = _module_sources_with_main_block()
    assert modules, "No points CLI modules found to validate."

    for module_path, source in modules:
        assert any(token in source for token in ALLOWED_BOOTSTRAP_TOKENS), (
            f"{module_path} should use build_cli_main(...) or run_cli_entrypoint(...)."
        )
        for token in DISALLOWED_MANUAL_TOKENS:
            assert token not in source, (
                f"{module_path} still contains manual CLI bootstrap token: {token}"
            )
