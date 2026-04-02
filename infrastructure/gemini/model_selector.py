import threading
import time

from infrastructure.gemini.model_config import ModelConfig
from infrastructure.gemini.model_state import ModelState


class ModelSelector:
    """Wybór dostępnego modelu z uwzględnieniem limitów i listy exclude."""

    def __init__(self, models: list[ModelConfig]) -> None:
        if not models:
            msg = "Lista modeli nie może być pusta."
            raise ValueError(msg)
        self._model_states = [ModelState(m) for m in models]
        self._rate_lock = threading.Lock()

    @property
    def model_states(self) -> list[ModelState]:
        return self._model_states

    def pick_model(self, *, exclude: set[str] | None = None) -> str | None:
        excluded = exclude or set()
        with self._rate_lock:
            now = time.monotonic()
            for state in self._model_states:
                if state.model in excluded:
                    continue
                if state.is_available(now):
                    return state.model
        return None

    def try_record_request(self, model: str) -> bool:
        """Atomically verifies model availability and records an API request."""
        with self._rate_lock:
            now = time.monotonic()
            for state in self._model_states:
                if state.model != model:
                    continue
                if not state.is_available(now):
                    return False
                state.record_request(now)
                return True
        return False
