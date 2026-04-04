"""Contract/static tests for protocol modules and selected CI scripts."""

from __future__ import annotations

import inspect
import types
from pathlib import Path

import pytest

from scrapers.base import contracts as base_contracts
from scrapers.base.export import contracts as export_contracts
from scrapers.circuits import schemas as circuits_schemas
from scrapers.seasons.sections import contracts as season_contracts
from scripts import check_architecture_rules as architecture_rules
from scripts import check_domain_terminology as domain_terminology

pytestmark = pytest.mark.contract


# ---- scrapers/base/contracts.py ----


def test_base_contracts_export_expected_protocols() -> None:
    """contract/static: module exports key protocol symbols."""
    assert hasattr(base_contracts, "RecordAssemblerProtocol")
    assert hasattr(base_contracts, "SectionExtractionServiceProtocol")
    assert base_contracts.RecordAssembler is base_contracts.RecordAssemblerProtocol


def test_record_assembler_protocol_signature_is_stable() -> None:
    """contract/static: assembler protocol has a single payload argument."""
    signature = inspect.signature(base_contracts.RecordAssemblerProtocol.assemble)
    assert tuple(signature.parameters) == ("self", "payload")


def test_section_extraction_protocol_signature_is_stable() -> None:
    """contract/static: section extractor protocol accepts soup argument."""
    signature = inspect.signature(
        base_contracts.SectionExtractionServiceProtocol.extract,
    )
    assert tuple(signature.parameters) == ("self", "soup")


# ---- scrapers/base/export/contracts.py ----


def test_export_contracts_protocols_exist() -> None:
    """contract/static: export protocol API is exposed."""
    assert hasattr(export_contracts, "ExporterProtocol")
    assert hasattr(export_contracts, "FieldnamesStrategyProtocol")
    assert hasattr(export_contracts, "DataFrameFormatterProtocol")


def test_exporter_protocol_method_signatures_are_stable() -> None:
    """contract/static: exporter methods keep keyword-only options."""
    to_json = inspect.signature(export_contracts.ExporterProtocol.to_json)
    assert tuple(to_json.parameters) == (
        "self",
        "result",
        "path",
        "indent",
        "include_metadata",
    )
    assert to_json.parameters["indent"].kind is inspect.Parameter.KEYWORD_ONLY
    assert to_json.parameters["include_metadata"].kind is inspect.Parameter.KEYWORD_ONLY

    to_csv = inspect.signature(export_contracts.ExporterProtocol.to_csv)
    assert tuple(to_csv.parameters) == (
        "self",
        "result",
        "path",
        "fieldnames",
        "include_metadata",
    )
    assert to_csv.parameters["fieldnames"].kind is inspect.Parameter.KEYWORD_ONLY
    assert to_csv.parameters["include_metadata"].kind is inspect.Parameter.KEYWORD_ONLY


def test_export_support_protocol_signatures_are_stable() -> None:
    """contract/static: formatter/fieldname contracts stay compatible."""
    resolve = inspect.signature(export_contracts.FieldnamesStrategyProtocol.resolve)
    assert tuple(resolve.parameters) == ("self", "data", "strategy")
    assert resolve.parameters["strategy"].kind is inspect.Parameter.KEYWORD_ONLY

    formatter = inspect.signature(export_contracts.DataFrameFormatterProtocol.format)
    assert tuple(formatter.parameters) == ("self", "result")


# ---- scrapers/seasons/sections/contracts.py + circuits schema ----


def test_season_section_protocol_parse_signature_is_stable() -> None:
    """contract/static: season section parser protocol accepts fragment."""
    signature = inspect.signature(season_contracts.SeasonSectionParser.parse)
    assert tuple(signature.parameters) == ("self", "section_fragment")


def test_build_circuits_schema_returns_shared_table_schema() -> None:
    """contract/static: schema builder returns canonical circuits table schema."""
    schema = circuits_schemas.build_circuits_schema()
    assert schema is circuits_schemas.TABLE_SCHEMA


# ---- scripts/check_architecture_rules.py ----


def test_detect_relevant_domains_uses_scrapers_prefix() -> None:
    """contract/static: detects only configured domains under scrapers/."""
    changed = [
        Path("scrapers/seasons/entrypoint.py"),
        Path("scrapers/circuits/schemas.py"),
        Path("tests/test_something.py"),
    ]

    detected = architecture_rules._detect_relevant_domains(  # noqa: SLF001
        changed,
        domains=("seasons", "circuits", "drivers"),
    )

    assert detected == {"seasons", "circuits"}


def test_check_required_layout_reports_missing_entrypoint_and_layers(
    tmp_path: Path,
) -> None:
    """contract/static: required layout reports missing files/layers."""
    root = tmp_path / "scrapers"
    (root / "seasons").mkdir(parents=True)

    rules = types.SimpleNamespace(
        REQUIRED_LAYERS_BY_DOMAIN={"seasons": ("app", "sections")},
    )
    rules.LAYERS = {"app", "sections"}
    rules.infer_layer = (
        lambda _path, domain: "app" if domain == "seasons" else "unknown"
    )

    violations = architecture_rules._check_required_layout(root, ("seasons",), rules)  # noqa: SLF001

    assert any("Missing facade entrypoint in domain: seasons" in v for v in violations)
    assert any("Missing layer modules for seasons" in v for v in violations)


def test_architecture_main_parses_paths_from_argv(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """contract/static: main() consumes positional paths via argparse."""
    monkeypatch.setattr(
        architecture_rules,
        "_load_architecture_rules",
        lambda: types.SimpleNamespace(
            DOMAINS=("seasons",),
            ENTRYPOINT_DOMAINS=("seasons",),
        ),
    )
    monkeypatch.setattr(
        architecture_rules,
        "_check_required_layout",
        lambda *_args, **_kwargs: [],
    )
    monkeypatch.setattr(
        architecture_rules,
        "_check_layer_boundaries",
        lambda *_args, **_kwargs: [],
    )
    monkeypatch.setattr(
        architecture_rules,
        "_check_sections_single_scraper_boundary",
        lambda *_args, **_kwargs: [],
    )
    monkeypatch.setattr(
        architecture_rules,
        "_check_cross_domain_imports",
        lambda *_args, **_kwargs: [],
    )

    captured: dict[str, list[Path]] = {}

    def fake_detect(paths: list[Path], *, domains: tuple[str, ...]) -> set[str]:
        captured["paths"] = paths
        captured["domains"] = list(domains)
        return set()

    monkeypatch.setattr(architecture_rules, "_detect_relevant_domains", fake_detect)
    monkeypatch.setattr(
        "sys.argv",
        ["check_architecture_rules.py", "scrapers/seasons/x.py", "README.md"],
    )

    result = architecture_rules.main()

    assert result == 0
    assert captured["paths"] == [Path("scrapers/seasons/x.py")]
    assert captured["domains"] == ["seasons"]


# ---- scripts/check_domain_terminology.py ----


def test_token_pattern_matches_whole_tokens_only() -> None:
    """contract/static: forbidden-term regex avoids substring matches."""
    pattern = domain_terminology._token_pattern("constructor")  # noqa: SLF001

    assert pattern.search("constructor standings")
    assert not pattern.search("constructors standings")


def test_run_check_returns_missing_glossary_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """contract/static: run_check reports when glossary is absent."""
    monkeypatch.setattr(domain_terminology, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(domain_terminology, "GLOSSARY_PATH", Path("missing.md"))

    assert domain_terminology.run_check() == ["missing glossary file: missing.md"]


def test_main_delegates_to_run_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    """contract/static: main() delegates execution through scripts run_cli wrapper."""
    called: dict[str, object] = {}
    expected_exit_code = 7

    def fake_run_cli(name: str, runner):
        called["name"] = name
        called["runner"] = runner
        return expected_exit_code

    monkeypatch.setattr(domain_terminology, "run_cli", fake_run_cli)

    result = domain_terminology.main(["--ignored"])

    assert result == expected_exit_code
    assert called["name"] == "domain-terminology"
    assert callable(called["runner"])
