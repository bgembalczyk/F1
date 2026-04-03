from typing import Any, Callable
from uuid import uuid4

from infrastructure.gemini.cache import GeminiCache
from infrastructure.gemini.model_selector import ModelSelector
from scrapers.base.logging import build_execution_context
from scrapers.base.logging import get_logger


class GeminiOrchestrationService:
    """Orkiestruje retry/fallback modeli i integrację z cache."""

    def __init__(
        self,
        *,
        model_selector: ModelSelector,
        cache: GeminiCache,
    ) -> None:
        self._model_selector = model_selector
        self._cache = cache
        self._logger = get_logger(self.__class__.__name__)

    def run(
        self,
        prompt: str,
        *,
        response_mime_type: str,
        call_api: Callable[[str], dict[str, Any]],
    ) -> dict[str, Any]:
        error_models: set[str] = set()
        run_id = str(uuid4())

        while True:
            model = self._model_selector.pick_model(exclude=error_models)
            if model is None:
                msg = (
                    "Wszystkie dostępne modele Gemini są wyczerpane "
                    "lub osiągnęły limit.\n"
                    f"Modele z błędem API: {error_models or '(brak)'}\n"
                    "Dostępne modele: "
                    f"{[s.model for s in self._model_selector.model_states]}"
                )
                raise RuntimeError(msg)

            cached = self._cache.get(prompt, model)
            context = build_execution_context(
                run_id=run_id,
                domain="gemini",
                seed_name="gemini_orchestration",
                source=model,
            )
            if cached is not None:
                self._logger.info("job_skip", extra=context)
                return cached

            if not self._model_selector.try_record_request(model):
                continue

            try:
                self._logger.info("job_start", extra=context)
                result = call_api(model)
            except Exception:  # noqa: BLE001
                error_models.add(model)
                continue

            self._cache.set(prompt, model, result)
            self._logger.info("job_end", extra=context)
            return result
