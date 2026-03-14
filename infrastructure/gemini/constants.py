from pathlib import Path

from infrastructure.gemini.model_config import ModelConfig

ONE_YEAR_SECONDS = 365 * 24 * 60 * 60

API_URL_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={api_key}"
)
DEFAULT_KEY_FILE = (
    Path(__file__).resolve().parents[2] / "config" / "gemini_api_key.txt"
)
DEFAULT_TIMEOUT = 30

# Domyślna lista modeli używana przez from_key_file() gdy models nie zostanie podane.
DEFAULT_MODELS: list[ModelConfig] = [
    ModelConfig(
        model="gemini-3-flash-preview",
        requests_per_minute=5,
        requests_per_day=20,
    ),
    ModelConfig(
        model="gemini-2.5-flash",
        requests_per_minute=5,
        requests_per_day=20,
    ),
    ModelConfig(
        model="gemini-3.1-flash-lite-preview",
        requests_per_minute=15,
        requests_per_day=500,
    ),
    ModelConfig(
        model="gemini-2.5-flash-lite",
        requests_per_minute=10,
        requests_per_day=20,
    ),
    ModelConfig(
        model="gemini-2.5-flash-lite-preview-09-2025",
        requests_per_minute=10,
        requests_per_day=20,
    ),
    ModelConfig(
        model="gemma-3-27b-it",
        requests_per_minute=30,
        requests_per_day=14400,
    ),
    ModelConfig(
        model="gemma-3-12b-it",
        requests_per_minute=30,
        requests_per_day=14400,
    ),
    ModelConfig(
        model="gemma-3-4b-it",
        requests_per_minute=30,
        requests_per_day=14400,
    ),
    ModelConfig(
        model="gemma-3-2b-it",
        requests_per_minute=30,
        requests_per_day=14400,
    ),
    ModelConfig(
        model="gemma-3-1b-it",
        requests_per_minute=30,
        requests_per_day=14400,
    ),
]
