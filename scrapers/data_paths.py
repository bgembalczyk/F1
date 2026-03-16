from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataPaths:
    data_root: Path = Path("data")
    raw_root: Path = Path("data/raw")
    normalized_root: Path = Path("data/normalized")
    checkpoints_root: Path = Path("data/checkpoints")
    legacy_wiki_root: Path = Path("data/wiki")

    def raw_path(self, *parts: str) -> Path:
        return self.raw_root.joinpath(*parts)

    def normalized_path(self, *parts: str) -> Path:
        return self.normalized_root.joinpath(*parts)

    def checkpoints_path(self, *parts: str) -> Path:
        return self.checkpoints_root.joinpath(*parts)

    def legacy_wiki_path(self, *parts: str) -> Path:
        return self.legacy_wiki_root.joinpath(*parts)

    def resolve_legacy_wiki_read(self, path: str | Path) -> Path:
        """Resolve `data/wiki/...` reads to new layout with legacy fallback."""
        relative = Path(path)
        if relative.is_absolute() and self.legacy_wiki_root in relative.parents:
            relative = relative.relative_to(self.legacy_wiki_root)
        elif str(relative).startswith("data/wiki/"):
            relative = relative.relative_to("data/wiki")

        candidate_new = self.raw_root / relative
        if candidate_new.exists():
            return candidate_new

        candidate_legacy = self.legacy_wiki_root / relative
        return candidate_legacy


def default_data_paths() -> DataPaths:
    return DataPaths()
