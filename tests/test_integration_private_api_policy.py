from __future__ import annotations

import re
from pathlib import Path

_PRIVATE_MEMBER_ACCESS = re.compile(r"\.\_[A-Za-z]")
_INTEGRATION_PATTERNS: tuple[str, ...] = (
    "test_domain_minimal_e2e",
    "test_driver_infobox_integration",
    "test_section_adapter_integration",
    "test_common_value_objects_integration",
)
_JUSTIFICATION_TAG = "PRIVATE-API-JUSTIFIED"


def _integration_tests() -> list[Path]:
    tests_dir = Path(__file__).parent
    files = sorted(tests_dir.glob("test_*.py"))
    return [
        path
        for path in files
        if any(pattern in path.name for pattern in _INTEGRATION_PATTERNS)
    ]


def test_integration_tests_do_not_use_slf001_file_noqa() -> None:
    violating = []
    for path in _integration_tests():
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
        if "SLF001" in first_line:
            violating.append(path.name)

    assert not violating, (
        "Integration tests cannot globally ignore SLF001. "
        f"Remove file-level ignore from: {violating}"
    )


def test_integration_tests_do_not_touch_private_api_without_justification() -> None:
    violations: list[str] = []
    for path in _integration_tests():
        for line_no, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if not _PRIVATE_MEMBER_ACCESS.search(line):
                continue
            if _JUSTIFICATION_TAG in line:
                continue
            violations.append(f"{path.name}:{line_no}")

    assert not violations, (
        "Integration tests should use public API. "
        "If private access is required, add explicit justification "
        f"tag '{_JUSTIFICATION_TAG}' on the same line. Violations: {violations}"
    )
