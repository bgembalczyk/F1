"""Generate PlantUML inheritance diagrams for the F1 project (v3 – fixed)."""

import ast
from collections import defaultdict
from collections import deque
from pathlib import Path

EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    ".idea",
    "node_modules",
    "venv",
    ".venv",
    "tests",
    "benchmarks",
    "artifacts",
}


def should_skip(p: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in p.parts)


all_defs: list[dict] = []
root = Path()
for py_file in sorted(root.rglob("*.py")):
    if should_skip(py_file):
        continue
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
    except Exception:
        continue
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(base.attr)
            elif isinstance(base, ast.Subscript):
                v = base.value
                if isinstance(v, ast.Name):
                    bases.append(v.id)
                elif isinstance(v, ast.Attribute):
                    bases.append(v.attr)
        all_defs.append({"name": node.name, "bases": bases, "file": str(py_file)})

by_name: dict[str, list[dict]] = defaultdict(list)
for d in all_defs:
    by_name[d["name"]].append(d)

all_names = set(by_name.keys())
info: dict[str, dict] = {n: defs[0] for n, defs in by_name.items()}

par: dict[str, set[str]] = defaultdict(set)
for name, d in info.items():
    for b in d["bases"]:
        if b in all_names and b != name:
            par[name].add(b)

chld: dict[str, set[str]] = defaultdict(set)
for child, ps in par.items():
    for p in ps:
        chld[p].add(child)

graph_nodes = set(par.keys()) | set(chld.keys())

# ──────────────────── helpers ─────────────────────────────────────────────────


def descendants(start: str, pool: set[str] | None = None) -> set[str]:
    result: set[str] = set()
    q = deque([start])
    while q:
        n = q.popleft()
        if n in result:
            continue
        if pool is not None and n not in pool:
            continue
        result.add(n)
        q.extend(chld.get(n, set()))
    return result


def component_of(name: str) -> set[str]:
    if name not in all_names:
        return set()
    comp: set[str] = set()
    q = deque([name])
    while q:
        n = q.popleft()
        if n in comp:
            continue
        comp.add(n)
        q.extend(chld.get(n, set()))
        q.extend(par.get(n, set()))
    return comp


def classify(name: str) -> str:
    if name.endswith("Protocol") or name.endswith("Contract"):
        return "interface"
    if (
        "ABC" in name
        or name.endswith("Base")
        or name.startswith("Base")
        or "Mixin" in name
    ):
        return "abstract class"
    return "class"


def make_puml(title: str, classes: list[str]) -> str:
    cls_set = set(classes)
    lines = [
        "@startuml",
        f"title {title}",
        "skinparam classAttributeIconSize 0",
        "hide empty members",
        "hide circle",
        "",
    ]
    for cls in sorted(cls_set):
        lines.append(f"{classify(cls)} {cls}")
    lines.append("")
    edges: set[tuple[str, str]] = set()
    for child in sorted(cls_set):
        for p in sorted(par.get(child, set())):
            if p in cls_set:
                e = (p, child)
                if e not in edges:
                    lines.append(f"{p} <|-- {child}")
                    edges.add(e)
    lines += ["", "@enduml"]
    return "\n".join(lines)


def read_assigned(out_root: Path) -> set[str]:
    assigned: set[str] = set()
    for f in out_root.rglob("*.puml"):
        for line in f.read_text().splitlines():
            s = line.strip()
            for kw in ("abstract class ", "class ", "interface "):
                if s.startswith(kw):
                    cls = s[len(kw) :].strip().split()[0]
                    assigned.add(cls)
    return assigned


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    n_cls = sum(
        1
        for l in content.splitlines()
        if (
            l.startswith("class ")
            or l.startswith("abstract class ")
            or l.startswith("interface ")
        )
    )
    print(f'  {path.relative_to("docs/uml/inheritance")}  ({n_cls} classes)')


# ──────────────────── output root ────────────────────────────────────────────
OUT = Path("docs/uml/inheritance")

# ══════════════════════════════════════════════════════════════════════════════
# BIG component: ParserABC (248 classes)
# ══════════════════════════════════════════════════════════════════════════════
main_comp = component_of("ParserABC")

# PARSERS/01 – Abstract contracts & HTML element layer
p01: set[str] = set()
p01 |= descendants("ParserABC", main_comp)
# Only generic utility classes kept in core (everything else goes to its domain diagram)
KEEP_IN_CORE = {
    "SoupParser",
    "SectionParserABC",
    "HeaderParser",
    "ContentTextParser",
}
# Classes that match the generic p01 filter but belong to a domain-specific diagram
P01_EXCLUDE = {
    # → p03 (scrapers)
    "ArticleTablesParserABC",
    # → p04 (domain section parsers)
    "SectionParserBase",
    "TableSectionParser",
    "BaseSeasonParser",
    "BaseDriverResultsSectionParser",
    # → p05 (table parsers)
    "TableParserABC",
    "TableCellParserABC",
    "TableRowParserABC",
    "InfoboxCollapsibleTableParserABC",
    "InfoboxNestedTableParserABC",
    # → p07 (misc / infobox field parsers)
    "InfoboxHtmlFieldParserABC",
    "InfoboxRowsParserABC",
    "InfoboxCellParserABC",
}
p01 = {
    c
    for c in p01
    if (
        (
            c.endswith("ABC")
            or c.endswith("Base")
            or c.startswith("Base")
            or "Mixin" in c
            or c in KEEP_IN_CORE
        )
        and not c.startswith(
            "Wiki",
        )  # Wiki-prefixed ABCs belong in 02_wiki_html_parsers
        and c not in P01_EXCLUDE
    )
}
write(
    OUT / "parsers/01_parser_abc_core.puml",
    make_puml("Parser ABC – Core Contracts & HTML Layer", sorted(p01)),
)

# PARSERS/02 – Wiki HTML parsers (non-table; WikiTable* classes belong in p05)
p02: set[str] = set()
p02 |= {
    c
    for c in main_comp
    if c.startswith("Wiki") and (c.endswith("ABC") or c.endswith("Base"))
}
# add concrete wiki parsers reachable from ABC/Base classes already in p02
changed = True
while changed:
    changed = False
    for cls in list(main_comp):
        if cls in p02:
            continue
        if cls.startswith("Wiki") and ("Parser" in cls or "Scraper" in cls):
            if any(parent in p02 for parent in par.get(cls, set())):
                p02.add(cls)
                changed = True
# WikiTable* classes form the table parser hierarchy and belong in p05
p02 = {c for c in p02 if "WikiTable" not in c}
# Also include direct concrete implementations of WikiXxx element ABCs
# (e.g. CircuitInfoboxParser, ListElementParser) so inheritance edges stay within p02.
# Exclude domain base classes (ending/starting with 'Base') and explicitly relocated classes.
for _cls in list(main_comp):
    if _cls in p02 or _cls in P01_EXCLUDE:
        continue
    if _cls.endswith("Base") or (_cls.startswith("Base") and not _cls.endswith("ABC")):
        continue
    if any(
        parent in p02 and parent.startswith("Wiki") and parent.endswith("ABC")
        for parent in par.get(_cls, set())
    ):
        p02.add(_cls)
write(
    OUT / "parsers/02_wiki_html_parsers.puml",
    make_puml("Wiki HTML Parser Hierarchy", sorted(p02)),
)

# PARSERS/03 – Scrapers
SCRAPER_ROOTS = [
    "ScraperLifecycleABC",
    "ListScraperContract",
    "TableScraperContract",
    "SectionAwareMixin",
    "WikiElementParsingMixin",
    "FetchOrchestrationMixin",
]
p03: set[str] = set()
for r in SCRAPER_ROOTS:
    p03 |= descendants(r, main_comp)
p03 |= {c for c in main_comp if "Scraper" in c}
p03 |= {
    "WikiScraper",
    "RecursiveSectionParser",
    "SectionAdapter",
    "BodyContentAssembler",
    "ArticleTablesParser",
    "ArticleTablesParserABC",
    "ArticleSectionTablesHtmlParser",
    "SeedListTableScraper",
} & (main_comp | all_names)
p03 -= p01 | p02
write(OUT / "parsers/03_scrapers.puml", make_puml("Scraper Hierarchy", sorted(p03)))

# PARSERS/04 – Domain section parsers
# SectionParserBase, TableSectionParser, BaseSeasonParser, BaseDriverResultsSectionParser
# are listed as SECTION_ROOTS and are excluded from p01 via P01_EXCLUDE, so they land here.
SECTION_ROOTS = [
    "SectionParserBase",
    "TableSectionParser",
    "ApplyForElementsMixin",
    "ExtractListItemsMixin",
    "NestedSectionHandlingMixin",
    "SectionTableParseMixin",
    "DeclarativeSectionTableParseMixin",
    "BaseDriverResultsSectionParser",
    "BaseSeasonParser",
]
p04: set[str] = set()
for r in SECTION_ROOTS:
    p04 |= descendants(r, main_comp)
p04 |= {
    c
    for c in main_comp
    if (
        "SectionParser" in c
        or c.endswith("SubSectionParser")
        or c.endswith("SubSubSectionParser")
        or c.endswith("SubSubSubSectionParser")
    )
}
p04 -= p01 | p02 | p03
write(
    OUT / "parsers/04_section_parsers_domain.puml",
    make_puml("Domain Section Parsers", sorted(p04)),
)

# PARSERS/05 – Table parsers (complete self-contained hierarchy)
# TableParserABC, WikiTableElementParserABC and their chains are excluded from p01/p02
# via P01_EXCLUDE and the WikiTable filter, so they land here naturally.
TABLE_ROOTS = [
    "WikiTableElementParserABC",
    "WikiTableBaseParser",
    "WikiTableHtmlParser",
    "HtmlTableParser",
    "TableCellExtractionMixin",
    "TableRowParsingMixin",
    "TableParserABC",
    "TableCellParserABC",
    "TableRowParserABC",
    "HeaderNormalizationMixin",
]
p05: set[str] = set()
for r in TABLE_ROOTS:
    p05 |= descendants(r, main_comp)
p05 |= {
    c
    for c in main_comp
    if "TableParser" in c and c not in ("SectionTablesHtmlParserABC",)
}
p05 -= p01 | p02 | p03 | p04
write(
    OUT / "parsers/05_table_parsers.puml",
    make_puml("Table Parser Hierarchy", sorted(p05)),
)

# PARSERS/06 – WikiSectionNodeParserABC (own component)
p06 = component_of("WikiSectionNodeParserABC")
write(
    OUT / "parsers/06_wiki_section_nodes.puml",
    make_puml("Wiki Section Node Parsers", sorted(p06)),
)

# PARSERS/07 – ALL remaining main-component classes not yet covered
covered_main = p01 | p02 | p03 | p04 | p05 | p06
p07 = main_comp - covered_main
# Also add ArticleTablesAssembler/ABC (their own small component)
p07 |= component_of("ArticleTablesAssembler")
# Add standalone parser contracts/ABCs not connected to the ParserABC hierarchy
for _extra in (
    "NestedChildParser",
    "StructureParser",
    "HasTableParserABC",
    "HasTableMapperABC",
    "SectionAssembler",
):
    p07 |= component_of(_extra)
write(
    OUT / "parsers/07_misc_parsers.puml",
    make_puml("Miscellaneous Parser Utilities", sorted(p07)),
)

# ══════════════════════════════════════════════════════════════════════════════
# COLUMNS
# ══════════════════════════════════════════════════════════════════════════════
write(
    OUT / "columns/01_columns.puml",
    make_puml("Column Hierarchy (BaseColumn)", sorted(component_of("BaseColumn"))),
)

# ══════════════════════════════════════════════════════════════════════════════
# MAPPERS
# ══════════════════════════════════════════════════════════════════════════════
write(
    OUT / "mappers/01_mappers.puml",
    make_puml("Mapper Hierarchy (MapperABC)", sorted(component_of("MapperABC"))),
)

# ══════════════════════════════════════════════════════════════════════════════
# RECORDS
# ══════════════════════════════════════════════════════════════════════════════
write(
    OUT / "records/01_record_factories.puml",
    make_puml("Record Factories", sorted(component_of("BaseRecordFactory"))),
)

write(
    OUT / "records/02_record_transformers.puml",
    make_puml("Record Transformers", sorted(component_of("RecordTransformer"))),
)

write(
    OUT / "records/03_record_validators.puml",
    make_puml("Record Validators", sorted(component_of("RecordValidator"))),
)

write(
    OUT / "records/04_record_strategies.puml",
    make_puml(
        "Record Split & Assembly Strategies",
        sorted(
            component_of("SplitRule")
            | component_of("RecordSplitStrategy")
            | component_of("RecordAssemblyStrategy")
            | component_of("BaseRecordAssembler"),
        ),
    ),
)

write(
    OUT / "records/05_value_objects_models.puml",
    make_puml(
        "Value Objects & Domain Models",
        sorted(
            component_of("ValueObject")
            | component_of("ValidatedModel")
            | component_of("DataContract")
            | component_of("CircuitBaseRecord")
            | component_of("LinkRecord"),
        ),
    ),
)

# ══════════════════════════════════════════════════════════════════════════════
# SERVICES
# ══════════════════════════════════════════════════════════════════════════════
write(
    OUT / "services/01_pipeline_services.puml",
    make_puml("Pipeline & Domain Services", sorted(component_of("PipelineService"))),
)

write(
    OUT / "services/02_base_components.puml",
    make_puml(
        "Base Components & Section Extraction Services",
        sorted(
            component_of("BaseComponent")
            | component_of("BaseSectionExtractionService"),
        ),
    ),
)

# ══════════════════════════════════════════════════════════════════════════════
# CLASSIFIERS + COMPLETE EXTRACTORS
# ══════════════════════════════════════════════════════════════════════════════
write(
    OUT / "components/01_classifiers.puml",
    make_puml(
        "Classifier Hierarchy (ClassifierABC)",
        sorted(component_of("ClassifierABC")),
    ),
)

write(
    OUT / "components/02_complete_extractors.puml",
    make_puml("Complete Data Extractors", sorted(component_of("BaseDataExtractor"))),
)

# ══════════════════════════════════════════════════════════════════════════════
# INFOBOX
# ══════════════════════════════════════════════════════════════════════════════
write(
    OUT / "infobox/01_orchestrators.puml",
    make_puml(
        "Infobox Orchestrators & Providers",
        sorted(
            component_of("InfoboxOrchestratorABC")
            | component_of("InfoboxSectionDiscoveryABC")
            | component_of("InfoboxExtractorABC")
            | component_of("ParsingBundleProviderABC")
            | component_of("ParsingBundle"),
        ),
    ),
)

write(
    OUT / "infobox/02_text_utils.puml",
    make_puml(
        "Circuit & Infobox Text Utilities",
        sorted(component_of("InfoboxTextUtils")),
    ),
)

# ══════════════════════════════════════════════════════════════════════════════
# INFRASTRUCTURE
# ══════════════════════════════════════════════════════════════════════════════
write(
    OUT / "infrastructure/01_errors.puml",
    make_puml(
        "Error Hierarchy",
        sorted(component_of("ScraperError") | component_of("RequestError")),
    ),
)

write(
    OUT / "infrastructure/02_http_cache.puml",
    make_puml(
        "HTTP Client, Cache & Rate Limiter",
        sorted(
            component_of("BaseHttpClient")
            | component_of("RetryPolicy")
            | component_of("FileTtlCacheAdapter")
            | component_of("TextCacheProtocol")
            | component_of("SourceAdapter")
            | component_of("RateLimiter"),
        ),
    ),
)

write(
    OUT / "infrastructure/03_layers.puml",
    make_puml(
        "Layers, Executors & Job Runners",
        sorted(
            component_of("BaseExecutor")
            | component_of("BaseOrchestrationFlow")
            | component_of("LayerZeroRunConfigFactoryProtocol")
            | component_of("LayerJobRunner")
            | component_of("BaseRegistryEntry")
            | component_of("MetadataBindingMixin"),
        ),
    ),
)

# ══════════════════════════════════════════════════════════════════════════════
# MISC – only truly unassigned classes (no duplicates!)
# ══════════════════════════════════════════════════════════════════════════════
assigned = read_assigned(OUT)
truly_unassigned = graph_nodes - assigned

# Don't add whole components – just add the unassigned classes themselves
# (edges will only be drawn between classes both in the set)
misc_classes: set[str] = set(truly_unassigned)

if misc_classes:
    write(
        OUT / "misc/01_misc_small.puml",
        make_puml("Miscellaneous Small Hierarchies", sorted(misc_classes)),
    )
else:
    print("  misc/01_misc_small.puml  (nothing to add – all classes covered!)")

# ──────────────────── coverage report ────────────────────────────────────────
print("\n=== Coverage ===")
final_assigned = read_assigned(OUT)
print(f"  Total in graph:   {len(graph_nodes)}")
print(f"  Covered in .puml: {len(final_assigned & graph_nodes)}")
missing = graph_nodes - final_assigned
if missing:
    print(f"  Not covered ({len(missing)}): {sorted(missing)}")
else:
    print("  All graph classes covered!")

# Duplicates check
all_files = list(OUT.rglob("*.puml"))
cls_file_count: dict[str, list[str]] = defaultdict(list)
for f in all_files:
    for line in f.read_text().splitlines():
        s = line.strip()
        for kw in ("abstract class ", "class ", "interface "):
            if s.startswith(kw):
                cls = s[len(kw) :].strip().split()[0]
                cls_file_count[cls].append(f.name)

dups = {cls: files for cls, files in cls_file_count.items() if len(files) > 1}
if dups:
    print(f"\nDuplicate classes ({len(dups)}):")
    for cls, files in sorted(dups.items())[:10]:
        print(f"  {cls}: {files}")
else:
    print("\nNo duplicate classes!")
