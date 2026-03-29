from collections.abc import Callable
from pathlib import Path
from typing import Protocol


class MirrorTargetPolicyProtocol(Protocol):
    def targets_for(self, *, source_category: str, year: int) -> tuple[Path, ...]: ...


class ConstructorsMirrorService:
    def __init__(
        self,
        *,
        mirror_target_policy: MirrorTargetPolicyProtocol,
        copy_file: Callable[[Path, Path], None],
        year_provider: Callable[[], int],
    ) -> None:
        self._mirror_target_policy = mirror_target_policy
        self._copy_file = copy_file
        self._year_provider = year_provider

    def mirror(self, base_wiki_dir: Path, source_json_path: Path) -> None:
        current_year = self._year_provider()
        source_category = source_json_path.parent.parent.name
        mirror_targets = self._mirror_target_policy.targets_for(
            source_category=source_category,
            year=current_year,
        )

        for mirror_target_path in mirror_targets:
            target_path = base_wiki_dir / mirror_target_path

            if target_path == source_json_path:
                continue

            target_path.parent.mkdir(parents=True, exist_ok=True)
            self._copy_file(source_json_path, target_path)
