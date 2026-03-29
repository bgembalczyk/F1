from collections.abc import Callable
from pathlib import Path

from layers.zero.helpers import LayerZeroPathBuilder


class ConstructorsMirrorService:
    def __init__(
        self,
        *,
        mirror_targets: tuple[tuple[str, str], ...],
        copy_file: Callable[[Path, Path], None],
        year_provider: Callable[[], int],
        path_builder: LayerZeroPathBuilder | None = None,
    ) -> None:
        self._mirror_targets = mirror_targets
        self._copy_file = copy_file
        self._year_provider = year_provider
        self._path_builder = path_builder or LayerZeroPathBuilder()

    def mirror(self, base_wiki_dir: Path, source_json_path: Path) -> None:
        current_year = self._year_provider()
        for target_category, target_name_template in self._mirror_targets:
            target_rel_path = self._path_builder.raw_file_path(
                target_category,
                target_name_template.format(year=current_year),
            )
            target_path = base_wiki_dir / target_rel_path

            if target_path == source_json_path:
                continue

            target_path.parent.mkdir(parents=True, exist_ok=True)
            self._copy_file(source_json_path, target_path)
