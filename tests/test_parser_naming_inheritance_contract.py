from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ClassInfo:
    module: str
    name: str
    bases: tuple[str, ...]
    parse_args: tuple[str, ...] | None
    is_protocol: bool
    is_abstract: bool


def _iter_parser_files(root: Path) -> list[Path]:
    return sorted((root / "scrapers" / "parsers").rglob("*.py"))


def _module_name(root: Path, file_path: Path) -> str:
    rel = file_path.relative_to(root).with_suffix("")
    return ".".join(rel.parts)


def _collect_classes(root: Path) -> dict[str, ClassInfo]:
    classes: dict[str, ClassInfo] = {}
    for py_file in _iter_parser_files(root):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        module = _module_name(root, py_file)
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue

            parse_args: tuple[str, ...] | None = None
            is_protocol = any(
                ast.unparse(base).endswith("Protocol")
                or "Protocol[" in ast.unparse(base)
                for base in node.bases
            )
            is_abstract = any(ast.unparse(base).endswith("ABC") for base in node.bases)
            for member in node.body:
                if isinstance(member, ast.FunctionDef) and member.name == "parse":
                    parse_args = tuple(arg.arg for arg in member.args.args)
                    break

            key = f"{module}.{node.name}"
            classes[key] = ClassInfo(
                module=module,
                name=node.name,
                bases=tuple(
                    ast.unparse(base).split(".")[-1].split("[", 1)[0]
                    for base in node.bases
                ),
                parse_args=parse_args,
                is_protocol=is_protocol,
                is_abstract=is_abstract,
            )
    return classes


def _inherits_from(
    class_info: ClassInfo,
    classes_by_name: dict[str, ClassInfo],
    expected_bases: set[str],
) -> bool:
    pending = list(class_info.bases)
    seen: set[str] = set()
    while pending:
        base_name = pending.pop()
        if base_name in seen:
            continue
        seen.add(base_name)
        if base_name in expected_bases:
            return True
        for info in classes_by_name.values():
            if info.name == base_name:
                pending.extend(info.bases)
    return False


def _has_parse(
    class_info: ClassInfo,
    classes_by_name: dict[str, ClassInfo],
) -> bool:
    if class_info.parse_args is not None:
        return True
    pending = list(class_info.bases)
    seen: set[str] = set()
    while pending:
        base_name = pending.pop()
        if base_name in seen:
            continue
        seen.add(base_name)
        for info in classes_by_name.values():
            if info.name == base_name:
                if info.parse_args is not None:
                    return True
                pending.extend(info.bases)
    return False


def test_parser_name_to_inheritance_and_interface_contract() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    classes = _collect_classes(repo_root)
    violations: list[str] = []

    for class_info in classes.values():
        if class_info.is_protocol or class_info.is_abstract:
            continue

        if class_info.name.endswith("TableParser"):
            if class_info.module in {
                "scrapers.parsers.infobox.collapsible_table",
                "scrapers.parsers.infobox.table",
                # HtmlTableParser is a general-purpose HTML table parser,
                # not wiki-specific; excluded from wiki-table contract.
                "scrapers.parsers.html_table",
                "scrapers.parsers.table.html_table",
                # F1StandingsTableParser is a domain-specific standings parser
                # that operates on raw Tag input, not a wiki table mapper.
                "scrapers.parsers.section.standings.f1_table",
            }:
                continue
            base_name_join = " ".join(class_info.bases)
            _table_parser_bases = {
                "WikiTableBaseMapper",
                "WikiTableHtmlParser",
                "WikiTableElementParserBase",
            }
            inherits_table_base = _inherits_from(
                class_info,
                classes,
                _table_parser_bases,
            ) or any(b in base_name_join for b in _table_parser_bases)
            if not inherits_table_base:
                violations.append(
                    f"{class_info.module}.{class_info.name}: TableParser musi "
                    "dziedziczyć po WikiTableBaseMapper, WikiTableHtmlParser "
                    "lub WikiTableElementParserBase",
                )
            if not _has_parse(class_info, classes):
                violations.append(
                    f"{class_info.module}.{class_info.name}: TableParser musi mieć "
                    "publiczne parse",
                )

        if class_info.name.endswith("Parser"):
            parser_contract_bases = {
                "Parser",
                "WikiParser",
                "BaseSectionParser",
                "InfoboxFieldParser",
                "AbstractTableFragmentParser",
                # Root ABC — any class tracing back to ParserABC is a valid parser
                "ParserABC",
                # Wiki-element ABCs (cover WikiTableParser, WikiInfoboxParser, etc.)
                "WikiTableParserABC",
                "WikiInfoboxParserABC",
                "WikiListParserABC",
                "WikiNavboxParserABC",
                "WikiFigureParserABC",
                "WikiSectionParserABC",
                "WikiSectionStructureParserABC",
                # Base classes for HTML element parsers
                "BaseHtmlElementParser",
                # Wiki section / table parser base contracts
                "WikiSectionParserBase",
                "WikiTableElementParserBase",
            }
            if not _inherits_from(class_info, classes, parser_contract_bases):
                violations.append(
                    f"{class_info.module}.{class_info.name}: Parser musi "
                    "implementować parserowe ABC (Parser/WikiParser/BaseSectionParser/"
                    "InfoboxFieldParser/AbstractTableFragmentParser)",
                )
            if not _has_parse(class_info, classes):
                violations.append(
                    f"{class_info.module}.{class_info.name}: Parser musi mieć "
                    "publiczne parse (lokalnie lub przez dziedziczenie)",
                )

        if class_info.name.endswith("ListParser"):
            if class_info.name == "ListParser":
                continue
            if not _inherits_from(
                class_info,
                classes,
                {"ListParser", "WikiListParser", "WikiListParserABC"},
            ):
                violations.append(
                    f"{class_info.module}.{class_info.name}: ListParser musi "
                    "dziedziczyć po ListParser, WikiListParser lub WikiListParserABC",
                )

        if class_info.name.endswith("SectionParser") and not class_info.name.endswith(
            "SubSectionParser"
        ):
            if (
                ".section.nested." in class_info.module
                or ".section.sublevels." in class_info.module
            ):
                continue
            if ".parsers.liveries." in class_info.module or class_info.module.endswith(
                ".section.sponsorship",
            ):
                continue
            if class_info.module.endswith(
                ".section.protocol"
            ) or class_info.module.endswith(
                ".section.section_parser_protocol",
            ):
                continue
            # Liveries / sponsorship section parsers use a different (soup-based)
            # interface and are governed by their own contracts.
            if class_info.module in {
                "scrapers.parsers.wiki.team_liveries_section",
                "scrapers.parsers.wiki.section.sponsorship",
            }:
                continue
            # RecursiveSectionParser is internal infrastructure for the nested-section
            # parsing engine and is not itself a user-facing concrete section parser.
            if class_info.module in {
                "scrapers.parsers.wiki.recursive",
            }:
                continue
            _section_parser_bases = {
                "SectionParser",
                "NestedWikiSectionParser",
                # Canonical runtime base introduced after initial contract was written
                "BaseSectionParser",
                # soup-based section parsers used outside the NestedWikiSectionParser tree
                "WikiSectionParserBase",
                # recursive heading-level parsers (HistorySectionParser, etc.)
                "BaseNestedSectionParser",
                # WikiParser is the root for all recursive/nested parsers
                "WikiParser",
            }
            if not _inherits_from(class_info, classes, _section_parser_bases):
                violations.append(
                    f"{class_info.module}.{class_info.name}: SectionParser musi "
                    "realizować kontrakt SectionParser",
                )
            if class_info.parse_args is not None and (
                len(class_info.parse_args) < 2
                or class_info.parse_args[1] != "section_fragment"
            ):
                # NestedWikiSectionParser-style parsers accept a Tag/list[Tag] element,
                # not a section_fragment BeautifulSoup.  Skip the signature check for
                # any parser that descends from the nested-parser tree.
                if not _inherits_from(
                    class_info,
                    classes,
                    {"NestedWikiSectionParser", "BaseNestedSectionParser"},
                ):
                    violations.append(
                        f"{class_info.module}.{class_info.name}: parse musi mieć sygnaturę "
                        "parse(section_fragment)",
                    )

    assert not violations, "Naruszenia kontraktu parserów:\n- " + "\n- ".join(
        sorted(violations),
    )
