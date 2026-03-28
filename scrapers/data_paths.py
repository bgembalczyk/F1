from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataPaths:
    base_dir: Path = Path("data")
    raw_dir_name: str = "raw"
    normalized_dir_name: str = "normalized"
    checkpoints_dir_name: str = "checkpoints"
    legacy_wiki_dir_name: str = "wiki"

    @property
    def raw(self) -> Path:
        return self._dir(self.raw_dir_name)

    @property
    def normalized(self) -> Path:
        return self._dir(self.normalized_dir_name)

    @property
    def checkpoints(self) -> Path:
        return self._dir(self.checkpoints_dir_name)

    @property
    def legacy_wiki(self) -> Path:
        return self._dir(self.legacy_wiki_dir_name)

    def raw_file(self, category: str, filename: str) -> Path:
        return self._file(self.raw, category, filename)

    def normalized_file(self, category: str, filename: str) -> Path:
        return self._file(self.normalized, category, filename)

    def checkpoint_file(self, filename: str) -> Path:
        return self._file(self.checkpoints, filename)

    def legacy_wiki_file(self, category: str, filename: str) -> Path:
        return self._file(self.legacy_wiki, category, filename)

    def compatible_input_candidates(
        self,
        category: str,
        filename: str,
    ) -> tuple[Path, ...]:
        return (
            self.raw_file(category, filename),
            self.legacy_wiki_file(category, filename),
        )

    def resolve_compatible_input(self, category: str, filename: str) -> Path | None:
        for candidate in self.compatible_input_candidates(category, filename):
            if candidate.exists():
                return candidate
        return None

    def _dir(self, dirname: str) -> Path:
        return self.base_dir / dirname

    @staticmethod
    def _file(base: Path, *parts: str) -> Path:
        return base.joinpath(*parts)


def default_data_paths(*, base_dir: Path = Path("data")) -> DataPaths:
    return DataPaths(base_dir=base_dir)
