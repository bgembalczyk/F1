from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DomainId:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower().replace(" ", "_")
        if not normalized or any(ch in normalized for ch in "/\\"):
            msg = f"Invalid domain/category identifier: {self.value!r}"
            raise ValueError(msg)
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class DataPaths:
    base_dir: Path = Path("data")
    raw_dir_name: str = "raw"
    normalized_dir_name: str = "normalized"
    checkpoints_dir_name: str = "checkpoints"
    audit_dir_name: str = "audit"
    legacy_wiki_dir_name: str = "wiki"

    @property
    def raw(self) -> Path:
        return self.base_dir / self.raw_dir_name

    @property
    def normalized(self) -> Path:
        return self.base_dir / self.normalized_dir_name

    @property
    def checkpoints(self) -> Path:
        return self.base_dir / self.checkpoints_dir_name

    @property
    def audit(self) -> Path:
        return self.base_dir / self.audit_dir_name

    @property
    def legacy_wiki(self) -> Path:
        return self.base_dir / self.legacy_wiki_dir_name

    def raw_file(self, category: str, filename: str) -> Path:
        return self.raw / str(DomainId(category)) / filename

    def raw_list_file(self, category: str, filename: str) -> Path:
        return self.raw / str(DomainId(category)) / "list" / filename

    def raw_seed_file(self, category: str, filename: str) -> Path:
        return self.raw / str(DomainId(category)) / "seeds" / filename

    def normalized_file(self, category: str, filename: str) -> Path:
        return self.normalized / str(DomainId(category)) / filename

    def checkpoint_file(self, filename: str) -> Path:
        return self.checkpoints / filename

    def checkpoint_filename(self, step_id: int, layer: str, domain: str) -> str:
        return f"step_{step_id}_{layer}_{DomainId(domain)}.json"

    def checkpoint_step_file(self, step_id: int, layer: str, domain: str) -> Path:
        return self.checkpoint_file(self.checkpoint_filename(step_id, layer, domain))

    def audit_file(self, filename: str) -> Path:
        return self.audit / filename

    def legacy_wiki_file(self, category: str, filename: str) -> Path:
        return self.legacy_wiki / str(DomainId(category)) / filename

    def compatible_input_candidates(self, category: str, filename: str) -> tuple[Path, ...]:
        return (
            self.raw_file(category, filename),
            self.legacy_wiki_file(category, filename),
        )

    def resolve_compatible_input(self, category: str, filename: str) -> Path | None:
        for candidate in self.compatible_input_candidates(category, filename):
            if candidate.exists():
                return candidate
        return None


def default_data_paths(*, base_dir: Path = Path("data")) -> DataPaths:
    return DataPaths(base_dir=base_dir)
