from typing import Any, Callable

from infrastructure.gemini.cache_service import GeminiCacheService
from infrastructure.gemini.model_selector import ModelSelector
from scrapers.base.errors import PipelineError
from scrapers.base.errors import normalize_pipeline_error


class GeminiOrchestrationService:
    """Orkiestruje retry/fallback modeli i integrację z cache."""

    def __init__(
        self,
        *,
        model_selector: ModelSelector,
        cache_service: GeminiCacheService,
    ) -> None:
        self._model_selector = model_selector
        self._cache_service = cache_service

    def run(
        self,
        prompt: str,
        *,
        response_mime_type: str,
        call_api: Callable[[str], dict[str, Any]],
    ) -> dict[str, Any]:
        error_models: set[str] = set()

        while True:
            model = self._model_selector.pick_model(exclude=error_models)
            if model is None:
                raise PipelineError(
                    message="All Gemini models are exhausted or rate-limited.",
                    code="gemini.models_exhausted",
                    domain="gemini",
                    source_name="gemini",
                )

            cached = self._cache_service.get(prompt, model)
            if cached is not None:
                print(
                    f"[GeminiClient] Cache hit (model={model}), pomijam wywołanie API.",
                )
                return cached

            if not self._model_selector.try_record_request(model):
                continue

            try:
                result = call_api(model)
            except Exception as exc:  # noqa: BLE001
                normalize_pipeline_error(
                    exc,
                    code="gemini.call_failed",
                    message="Gemini model call failed.",
                    domain="gemini",
                    source_name=model,
                )
                error_models.add(model)
                continue

            self._cache_service.set(prompt, model, result)
            return result
