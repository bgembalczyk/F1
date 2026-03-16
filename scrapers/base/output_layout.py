from pathlib import Path


DATA_ROOT = Path("../../data")
LEGACY_WIKI_ROOT = DATA_ROOT / "wiki"


def output_dir_for(*, category: str, layer: str, root: Path = DATA_ROOT) -> Path:
    """Mapuje kategorię i warstwę pipeline na katalog wyjściowy."""
    return root / layer / category


def output_targets(
    *,
    category: str,
    layer: str,
    legacy_enabled: bool,
    legacy_root: Path = LEGACY_WIKI_ROOT,
) -> list[Path]:
    targets = [output_dir_for(category=category, layer=layer)]
    if legacy_enabled:
        targets.append(legacy_root)
    return targets

