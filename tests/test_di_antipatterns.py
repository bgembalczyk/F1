from __future__ import annotations

from pathlib import Path

from scripts.check_di_antipatterns import run_check


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_detects_service_creation_inside_business_method(tmp_path: Path) -> None:
    source = _write(
        tmp_path / "sample.py",
        """
class DriverPipeline:
    def process(self) -> None:
        parser = SectionService()
        parser.run()
""",
    )

    violations = run_check([source])

    assert len(violations) == 1
    violation = violations[0]
    assert violation.class_name == "DriverPipeline"
    assert violation.method_name == "process"
    assert violation.dependency_name == "SectionService"


def test_skips_creation_in_constructor_and_factory_methods(tmp_path: Path) -> None:
    source = _write(
        tmp_path / "sample.py",
        """
class DriverPipeline:
    def __init__(self) -> None:
        self.service = SectionService()

    def build_service(self):
        return SectionService()
""",
    )

    violations = run_check([source])

    assert violations == []


def test_allows_explicit_suppression_comment(tmp_path: Path) -> None:
    source = _write(
        tmp_path / "sample.py",
        """
class DriverPipeline:
    def process(self) -> None:
        # di-antipattern-allow: temporary migration shim
        service = LegacyClient()
        service.run()
""",
    )

    violations = run_check([source])

    assert violations == []
