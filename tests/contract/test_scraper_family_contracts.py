from __future__ import annotations

import ast
import importlib.util
import inspect
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_PATH = ROOT / "scrapers/family_contracts.py"


def _load_family_contracts_module():
    spec = importlib.util.spec_from_file_location("scrapers.family_contracts", CONTRACTS_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


FAMILY_CONTRACT_CASES = [
    (
        "ListScraperContract",
        ("fetch",),
        (
            "fetch",
            "_parse_soup",
        ),
    ),
    (
        "TableScraperContract",
        ("parse_soup", "parse_row"),
        (
            "parse_soup",
            "parse_row",
            "_parse_soup",
        ),
    ),
    (
        "SingleArticleScraperContract",
        ("extract_by_url", "_assemble_record"),
        (
            "extract_by_url",
            "_assemble_record",
            "_build_infobox_payload",
            "_build_tables_payload",
            "_build_sections_payload",
            "_before_payload_build",
            "_after_record_assembled",
            "_should_parse_article",
            "_prepare_article_soup",
        ),
    ),
    (
        "SectionParserContract",
        ("parse",),
        ("parse",),
    ),
]


@pytest.mark.contract
def test_scraper_family_contracts_are_exposed() -> None:
    family_contracts = _load_family_contracts_module()
    exported = set(getattr(family_contracts, "__all__", ()))
    assert exported == {
        "ListScraperContract",
        "TableScraperContract",
        "SingleArticleScraperContract",
        "SectionParserContract",
    }


@pytest.mark.contract
@pytest.mark.parametrize(
    ("contract_name", "required_methods", "_allowed_hooks"),
    FAMILY_CONTRACT_CASES,
)
def test_family_contract_methods_exist(
    contract_name: str,
    required_methods: tuple[str, ...],
    _allowed_hooks: tuple[str, ...],
) -> None:
    family_contracts = _load_family_contracts_module()
    contract = getattr(family_contracts, contract_name)
    for method_name in required_methods:
        assert callable(getattr(contract, method_name, None))


@pytest.mark.contract
@pytest.mark.parametrize(
    ("contract_name", "_required_methods", "allowed_hooks"),
    FAMILY_CONTRACT_CASES,
)
def test_family_contract_docstring_defines_extension_rules(
    contract_name: str,
    _required_methods: tuple[str, ...],
    allowed_hooks: tuple[str, ...],
) -> None:
    family_contracts = _load_family_contracts_module()
    contract = getattr(family_contracts, contract_name)
    doc = inspect.getdoc(contract) or ""
    assert "Extension rules" in doc
    for hook in allowed_hooks:
        if hook.startswith("_"):
            assert hook in doc


@pytest.mark.contract
@pytest.mark.parametrize(
    ("file_path", "class_name", "required_methods"),
    [
        ("scrapers/seed_list_scraper_table.py", "SeedListTableScraper", ("fetch",)),
        (
            "scrapers/scraper_table.py",
            "F1TableScraper",
            ("parse_soup", "parse_row"),
        ),
        (
            "scrapers/single_wiki_article/base.py",
            "SingleWikiArticleScraperBase",
            ("extract_by_url", "_assemble_record"),
        ),
        (
            "scrapers/parsers/section/protocol.py",
            "SectionParser",
            ("parse",),
        ),
    ],
)
def test_core_family_classes_expose_minimal_contract_methods(
    file_path: str,
    class_name: str,
    required_methods: tuple[str, ...],
) -> None:
    module = ast.parse((ROOT / file_path).read_text(encoding="utf-8"))
    class_node = next(
        node
        for node in module.body
        if isinstance(node, ast.ClassDef) and node.name == class_name
    )
    class_methods = {
        node.name
        for node in class_node.body
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
    }
    for method_name in required_methods:
        assert method_name in class_methods
