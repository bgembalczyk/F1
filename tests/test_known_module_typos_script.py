import subprocess
import sys

from scripts.lib import known_typos


def test_validate_target_packages_for_single_rule(tmp_path):
    package = tmp_path / "sample_package"
    package.mkdir()
    (package / "constants.py").write_text("# ok\n", encoding="utf-8")

    single_rule = known_typos.TypoRule(
        target_packages=(package,),
        expected_module_name="constants.py",
        disallowed_typo_name="contants.py",
        disallowed_import="sample.contants",
    )

    assert known_typos._validate_target_packages((single_rule,)) == []


def test_cli_script_runs_without_module_import_errors():
    command = [sys.executable, "scripts/check_known_module_typos.py"]
    result = subprocess.run(command, check=False, capture_output=True, text=True)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ModuleNotFoundError" not in result.stdout + result.stderr
