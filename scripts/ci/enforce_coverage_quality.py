from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from defusedxml import ElementTree

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Violation:
    message: str


@dataclass(frozen=True)
class GateInputs:
    global_coverage: float
    current_file_coverages: dict[str, float]
    changed_files: set[str]
    legacy_files: set[str]
    baseline_file_coverages: dict[str, object]
    threshold_path: list[float]
    current_sprint: int
    current_threshold: float
    legacy_improvement: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Coverage quality gate: patch no-regression, global progressive threshold, "
            "legacy low-coverage touched-file improvement."
        ),
    )
    parser.add_argument("--coverage-xml", default="coverage.xml")
    parser.add_argument("--baseline", default=".ci/coverage-baseline.json")
    parser.add_argument("--policy", default=".ci/coverage-policy.json")
    parser.add_argument("--legacy-files", default=".ci/legacy-low-coverage-files.txt")
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _to_percent(raw_rate: float) -> float:
    return round(raw_rate * 100.0, 2)


def _parse_coverage(coverage_xml: Path) -> tuple[float, dict[str, float]]:
    tree = ElementTree.parse(coverage_xml)
    root = tree.getroot()

    global_rate = float(root.attrib.get("line-rate", "0"))
    global_percent = _to_percent(global_rate)

    file_coverages: dict[str, float] = {}
    for class_el in root.findall(".//class"):
        filename = class_el.attrib.get("filename")
        if not filename:
            continue
        normalized = Path(filename).as_posix()
        line_rate = float(class_el.attrib.get("line-rate", "0"))
        file_coverages[normalized] = _to_percent(line_rate)

    return global_percent, file_coverages


def _git_changed_files(base_sha: str, head_sha: str) -> set[str]:
    cmd = ["git", "diff", "--name-only", "--diff-filter=AMR", base_sha, head_sha]
    out = subprocess.check_output(cmd, cwd=REPO_ROOT, text=True)
    return {line.strip() for line in out.splitlines() if line.strip()}


def _load_legacy_files(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {
        Path(raw.strip()).as_posix()
        for raw in path.read_text(encoding="utf-8").splitlines()
        if raw.strip() and not raw.strip().startswith("#")
    }


def _validate_progressive_threshold(policy: dict[str, object]) -> list[Violation]:
    violations: list[Violation] = []
    thresholds = policy.get("global_threshold_path")
    if not isinstance(thresholds, list) or not thresholds:
        return [Violation("Brak poprawnej global_threshold_path w policy JSON.")]

    try:
        threshold_values = [float(value) for value in thresholds]
        current_sprint = int(policy.get("current_sprint", 1))
        min_increment = float(policy.get("minimum_global_increment_per_sprint_pp", 0))
    except (TypeError, ValueError):
        return [
            Violation("Niepoprawne typy w coverage policy (sprint/progi/przyrost)."),
        ]

    for index in range(1, len(threshold_values)):
        if threshold_values[index] <= threshold_values[index - 1]:
            violations.append(
                Violation(
                    "global_threshold_path musi być ściśle rosnąca "
                    f"(problem na pozycji {index + 1})."
                )
            )

    for index in range(1, len(threshold_values)):
        delta = threshold_values[index] - threshold_values[index - 1]
        if delta < min_increment:
            violations.append(
                Violation(
                    "Minimalny przyrost globalny na sprint jest za mały: "
                    f"sprint {index}→{index + 1} ma {delta:.2f} pp, "
                    f"wymagane >= {min_increment:.2f} pp."
                )
            )

    if current_sprint < 1 or current_sprint > len(threshold_values):
        violations.append(
            Violation(
                "current_sprint poza zakresem global_threshold_path "
                f"(1..{len(threshold_values)})."
            )
        )
    return violations


def _load_gate_inputs(args: argparse.Namespace) -> GateInputs:
    coverage_xml = REPO_ROOT / args.coverage_xml
    baseline_json = REPO_ROOT / args.baseline
    policy_json = REPO_ROOT / args.policy
    legacy_files_txt = REPO_ROOT / args.legacy_files

    policy = _load_json(policy_json)
    baseline = _load_json(baseline_json)

    global_coverage, current_file_coverages = _parse_coverage(coverage_xml)
    changed_files = _git_changed_files(args.base_sha, args.head_sha)
    legacy_files = _load_legacy_files(legacy_files_txt)

    threshold_path = [float(value) for value in policy["global_threshold_path"]]
    current_sprint = int(policy["current_sprint"])
    current_threshold = threshold_path[current_sprint - 1]

    baseline_file_coverages = baseline.get("file_coverages", {})
    if not isinstance(baseline_file_coverages, dict):
        baseline_file_coverages = {}

    legacy_improvement = float(policy.get("legacy_minimum_improvement_pp", 0.5))

    return GateInputs(
        global_coverage=global_coverage,
        current_file_coverages=current_file_coverages,
        changed_files=changed_files,
        legacy_files=legacy_files,
        baseline_file_coverages=baseline_file_coverages,
        threshold_path=threshold_path,
        current_sprint=current_sprint,
        current_threshold=current_threshold,
        legacy_improvement=legacy_improvement,
    )


def _evaluate_global_threshold(inputs: GateInputs) -> list[Violation]:
    if inputs.global_coverage >= inputs.current_threshold:
        return []
    return [
        Violation(
            f"Global coverage {inputs.global_coverage:.2f}% < próg sprintu "
            f"{inputs.current_sprint} ({inputs.current_threshold:.2f}%)."
        )
    ]


def _evaluate_changed_files(inputs: GateInputs) -> list[Violation]:
    violations: list[Violation] = []

    for changed_file in sorted(inputs.changed_files):
        if not changed_file.endswith(".py"):
            continue
        if changed_file not in inputs.current_file_coverages:
            continue

        current_cov = float(inputs.current_file_coverages[changed_file])
        baseline_cov_raw = inputs.baseline_file_coverages.get(changed_file)
        if baseline_cov_raw is None:
            continue

        baseline_cov = float(baseline_cov_raw)
        if current_cov < baseline_cov:
            violations.append(
                Violation(
                    f"Patch coverage regression: {changed_file} spadł z "
                    f"{baseline_cov:.2f}% do {current_cov:.2f}%."
                )
            )

        if (
            changed_file in inputs.legacy_files
            and current_cov < baseline_cov + inputs.legacy_improvement
        ):
            violations.append(
                Violation(
                    f"Legacy low coverage '{changed_file}' został dotknięty, "
                    f"ale poprawa to tylko {current_cov - baseline_cov:.2f} pp; "
                    f"wymagane >= {inputs.legacy_improvement:.2f} pp."
                )
            )

    return violations


def _format_and_print_result(inputs: GateInputs, violations: list[Violation]) -> int:
    if violations:
        print("Coverage quality gate: FAILED")
        for violation in violations:
            print(f"- {violation.message}")
        return 1

    print("Coverage quality gate: OK")
    print(
        f"Global coverage: {inputs.global_coverage:.2f}% (sprint "
        f"{inputs.current_sprint}, próg {inputs.current_threshold:.2f}%)."
    )
    return 0


def main() -> int:
    args = parse_args()
    inputs = _load_gate_inputs(args)

    policy = _load_json(REPO_ROOT / args.policy)
    violations = _validate_progressive_threshold(policy)
    violations.extend(_evaluate_global_threshold(inputs))
    violations.extend(_evaluate_changed_files(inputs))

    return _format_and_print_result(inputs, violations)


if __name__ == "__main__":
    sys.exit(main())
