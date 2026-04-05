# ruff: noqa: SLF001
"""Unit tests for scripts/ci/enforce_coverage_quality.py."""
from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING
from typing import Any

import pytest

from scripts.ci import enforce_coverage_quality as ecq

if TYPE_CHECKING:
    from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_inputs(**kwargs: Any) -> ecq.GateInputs:
    defaults: dict[str, Any] = {
        "global_coverage": 90.0,
        "current_file_coverages": {},
        "changed_files": set(),
        "legacy_files": set(),
        "baseline_file_coverages": {},
        "threshold_path": [85.0, 88.0, 91.0],
        "current_sprint": 1,
        "current_threshold": 85.0,
        "legacy_improvement": 0.5,
    }
    defaults.update(kwargs)
    return ecq.GateInputs(**defaults)


# ---------------------------------------------------------------------------
# _to_percent
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_to_percent_converts_rate_to_percentage() -> None:
    assert ecq._to_percent(0.9) == pytest.approx(90.0)
    assert ecq._to_percent(0.0) == pytest.approx(0.0)
    assert ecq._to_percent(1.0) == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# _parse_coverage
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_parse_coverage_reads_global_and_file_rates(tmp_path: Path) -> None:
    xml_content = dedent("""\
        <?xml version="1.0" ?>
        <coverage version="7" line-rate="0.85" branch-rate="0.7" timestamp="0">
          <packages>
            <package name=".">
              <classes>
                <class name="module.py" filename="src/module.py"
                       line-rate="0.9" branch-rate="0.8">
                  <methods/>
                  <lines/>
                </class>
              </classes>
            </package>
          </packages>
        </coverage>
    """)
    xml_path = tmp_path / "coverage.xml"
    xml_path.write_text(xml_content, encoding="utf-8")

    global_cov, file_covs = ecq._parse_coverage(xml_path)

    assert global_cov == pytest.approx(85.0)
    assert "src/module.py" in file_covs
    assert file_covs["src/module.py"] == pytest.approx(90.0)


@pytest.mark.unit
def test_parse_coverage_handles_missing_line_rate(tmp_path: Path) -> None:
    xml_content = dedent("""\
        <?xml version="1.0" ?>
        <coverage version="7" timestamp="0">
          <packages/>
        </coverage>
    """)
    xml_path = tmp_path / "coverage.xml"
    xml_path.write_text(xml_content, encoding="utf-8")

    global_cov, file_covs = ecq._parse_coverage(xml_path)

    assert global_cov == 0.0
    assert file_covs == {}


@pytest.mark.unit
def test_parse_coverage_skips_class_without_filename(tmp_path: Path) -> None:
    xml_content = dedent("""\
        <?xml version="1.0" ?>
        <coverage version="7" line-rate="0.9" branch-rate="0.8" timestamp="0">
          <packages>
            <package name=".">
              <classes>
                <class name="no_file" line-rate="0.5" branch-rate="0.4">
                  <methods/>
                  <lines/>
                </class>
              </classes>
            </package>
          </packages>
        </coverage>
    """)
    xml_path = tmp_path / "coverage.xml"
    xml_path.write_text(xml_content, encoding="utf-8")

    _, file_covs = ecq._parse_coverage(xml_path)
    assert file_covs == {}


# ---------------------------------------------------------------------------
# _load_legacy_files
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_load_legacy_files_returns_empty_if_missing(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.txt"
    assert ecq._load_legacy_files(missing) == set()


@pytest.mark.unit
def test_load_legacy_files_parses_file(tmp_path: Path) -> None:
    txt = tmp_path / "legacy.txt"
    txt.write_text(
        "# comment\nsrc/module.py\n\nother/file.py\n",
        encoding="utf-8",
    )
    result = ecq._load_legacy_files(txt)
    assert result == {"src/module.py", "other/file.py"}



# ---------------------------------------------------------------------------
# _validate_progressive_threshold
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_validate_progressive_threshold_valid_policy() -> None:
    policy = {
        "global_threshold_path": [80.0, 85.0, 90.0],
        "current_sprint": 2,
        "minimum_global_increment_per_sprint_pp": 1.5,
    }
    violations = ecq._validate_progressive_threshold(policy)
    assert violations == []


@pytest.mark.unit
def test_validate_progressive_threshold_not_strictly_increasing() -> None:
    policy = {
        "global_threshold_path": [85.0, 85.0, 90.0],
        "current_sprint": 1,
        "minimum_global_increment_per_sprint_pp": 1.5,
    }
    violations = ecq._validate_progressive_threshold(policy)
    assert any("ściśle rosnąca" in v.message for v in violations)


@pytest.mark.unit
def test_validate_progressive_threshold_increment_too_small() -> None:
    policy = {
        "global_threshold_path": [85.0, 86.0, 90.0],
        "current_sprint": 1,
        "minimum_global_increment_per_sprint_pp": 2.0,
    }
    violations = ecq._validate_progressive_threshold(policy)
    assert any("przyrost" in v.message for v in violations)


@pytest.mark.unit
def test_validate_progressive_threshold_sprint_out_of_range() -> None:
    policy = {
        "global_threshold_path": [85.0, 88.0],
        "current_sprint": 5,
        "minimum_global_increment_per_sprint_pp": 1.5,
    }
    violations = ecq._validate_progressive_threshold(policy)
    assert any("zakresem" in v.message for v in violations)


@pytest.mark.unit
def test_validate_progressive_threshold_missing_path() -> None:
    policy: dict[str, Any] = {
        "current_sprint": 1,
        "minimum_global_increment_per_sprint_pp": 1.5,
    }
    violations = ecq._validate_progressive_threshold(policy)
    assert any("global_threshold_path" in v.message for v in violations)


@pytest.mark.unit
def test_validate_progressive_threshold_invalid_types() -> None:
    policy: dict[str, Any] = {
        "global_threshold_path": ["bad", "values"],
        "current_sprint": "x",
        "minimum_global_increment_per_sprint_pp": "y",
    }
    violations = ecq._validate_progressive_threshold(policy)
    assert any("Niepoprawne typy" in v.message for v in violations)


# ---------------------------------------------------------------------------
# _evaluate_global_threshold
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_evaluate_global_threshold_passes_when_above_threshold() -> None:
    inputs = _make_inputs(global_coverage=86.0, current_threshold=85.0)
    assert ecq._evaluate_global_threshold(inputs) == []


@pytest.mark.unit
def test_evaluate_global_threshold_passes_at_exact_threshold() -> None:
    inputs = _make_inputs(global_coverage=85.0, current_threshold=85.0)
    assert ecq._evaluate_global_threshold(inputs) == []


@pytest.mark.unit
def test_evaluate_global_threshold_fails_when_below() -> None:
    inputs = _make_inputs(global_coverage=76.15, current_threshold=85.0)
    violations = ecq._evaluate_global_threshold(inputs)
    assert len(violations) == 1
    assert "76.15" in violations[0].message
    assert "85.00" in violations[0].message


# ---------------------------------------------------------------------------
# _evaluate_changed_files
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_evaluate_changed_files_no_violations_when_no_regression() -> None:
    inputs = _make_inputs(
        changed_files={"src/module.py"},
        current_file_coverages={"src/module.py": 90.0},
        baseline_file_coverages={"src/module.py": 85.0},
    )
    assert ecq._evaluate_changed_files(inputs) == []


@pytest.mark.unit
def test_evaluate_changed_files_regression_detected() -> None:
    inputs = _make_inputs(
        changed_files={"src/module.py"},
        current_file_coverages={"src/module.py": 80.0},
        baseline_file_coverages={"src/module.py": 90.0},
    )
    violations = ecq._evaluate_changed_files(inputs)
    assert len(violations) == 1
    assert "Patch coverage regression" in violations[0].message
    assert "src/module.py" in violations[0].message


@pytest.mark.unit
def test_evaluate_changed_files_skips_non_python() -> None:
    inputs = _make_inputs(
        changed_files={"README.md", "data.json"},
        current_file_coverages={},
        baseline_file_coverages={},
    )
    assert ecq._evaluate_changed_files(inputs) == []


@pytest.mark.unit
def test_evaluate_changed_files_skips_if_no_baseline() -> None:
    inputs = _make_inputs(
        changed_files={"src/new_file.py"},
        current_file_coverages={"src/new_file.py": 50.0},
        baseline_file_coverages={},
    )
    assert ecq._evaluate_changed_files(inputs) == []


@pytest.mark.unit
def test_evaluate_changed_files_legacy_improvement_required() -> None:
    inputs = _make_inputs(
        changed_files={"src/legacy.py"},
        current_file_coverages={"src/legacy.py": 60.1},
        baseline_file_coverages={"src/legacy.py": 60.0},
        legacy_files={"src/legacy.py"},
        legacy_improvement=0.5,
    )
    violations = ecq._evaluate_changed_files(inputs)
    assert len(violations) == 1
    assert "Legacy low coverage" in violations[0].message
    assert "src/legacy.py" in violations[0].message


@pytest.mark.unit
def test_evaluate_changed_files_legacy_improvement_sufficient() -> None:
    inputs = _make_inputs(
        changed_files={"src/legacy.py"},
        current_file_coverages={"src/legacy.py": 61.0},
        baseline_file_coverages={"src/legacy.py": 60.0},
        legacy_files={"src/legacy.py"},
        legacy_improvement=0.5,
    )
    violations = ecq._evaluate_changed_files(inputs)
    assert not any("legacy" in v.message.lower() for v in violations)


@pytest.mark.unit
def test_evaluate_changed_files_skips_missing_from_current() -> None:
    inputs = _make_inputs(
        changed_files={"src/module.py"},
        current_file_coverages={},
        baseline_file_coverages={"src/module.py": 80.0},
    )
    assert ecq._evaluate_changed_files(inputs) == []


# ---------------------------------------------------------------------------
# _format_and_print_result
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_format_and_print_result_ok(capsys: pytest.CaptureFixture[str]) -> None:
    inputs = _make_inputs(
        global_coverage=90.0,
        current_sprint=1,
        current_threshold=85.0,
    )
    ret = ecq._format_and_print_result(inputs, [])
    assert ret == 0
    out = capsys.readouterr().out
    assert "OK" in out


@pytest.mark.unit
def test_format_and_print_result_failed(capsys: pytest.CaptureFixture[str]) -> None:
    inputs = _make_inputs(
        global_coverage=70.0,
        current_sprint=1,
        current_threshold=85.0,
    )
    violations = [ecq.Violation("Test violation message")]
    ret = ecq._format_and_print_result(inputs, violations)
    assert ret == 1
    out = capsys.readouterr().out
    assert "FAILED" in out
    assert "Test violation message" in out


# ---------------------------------------------------------------------------
# _load_json
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_load_json_reads_and_parses(tmp_path: Path) -> None:
    json_path = tmp_path / "data.json"
    json_path.write_text('{"key": "value", "num": 42}', encoding="utf-8")
    result = ecq._load_json(json_path)
    assert result == {"key": "value", "num": 42}
