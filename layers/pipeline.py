from pathlib import Path

from layers.orchestration.protocols import LayerExecutorProtocol
from layers.zero.run_profile_paths import build_debug_run_config
from scrapers.base.run_config import RunConfig


class WikiPipelineApplication:
    """Aplikacja uruchamiająca workflow warstw 0 i 1.

    Wejście: zależności wykonawców warstw i ścieżki bazowe.
    Wyjście: metody uruchamiające generują artefakty w katalogu wyjściowym.
    """

    def __init__(
        self,
        *,
        base_wiki_dir: Path,
        base_debug_dir: Path,
        layer_zero_executor: LayerExecutorProtocol,
        layer_one_executor: LayerExecutorProtocol,
    ) -> None:
        self._base_wiki_dir = base_wiki_dir
        self._base_debug_dir = base_debug_dir
        self._layer_zero_executor = layer_zero_executor
        self._layer_one_executor = layer_one_executor

    def _build_run_config(self, *, profile: str = "debug") -> RunConfig:
        """Build konfigurację uruchomienia dla wskazanego profilu.

        Wejście: nazwa profilu (`debug`).
        Wyjście: obiekt `RunConfig`.
        """
        if profile == "debug":
            return build_debug_run_config(
                base_wiki_dir=self._base_wiki_dir,
                base_debug_dir=self._base_debug_dir,
            )
        raise ValueError(profile)

    def run_layer_zero(self) -> None:
        """Run workflow layer-0.

        Wejście: brak (korzysta z konfiguracji debug).
        Wyjście: brak (efekt uboczny: artefakty layer-0).
        """
        run_config = self._build_run_config()
        self._layer_zero_executor.run(run_config, self._base_wiki_dir)

    def run_layer_one(self) -> None:
        """Run workflow layer-1.

        Wejście: brak (korzysta z konfiguracji debug).
        Wyjście: brak (efekt uboczny: artefakty layer-1).
        """
        run_config = self._build_run_config()
        self._layer_one_executor.run(run_config, self._base_wiki_dir)
