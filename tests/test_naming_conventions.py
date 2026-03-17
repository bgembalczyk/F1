import importlib
import sys
from pathlib import Path

from scrapers.base.constants import NAMING_CONVENTIONS
from scrapers.base.constants import SCRAPER_CONSTANT_PREFIXES

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


def test_scraper_constants_follow_prefix_and_suffix_conventions():
    suffixes = tuple(convention["suffix"] for convention in NAMING_CONVENTIONS.values())
    for module_path, prefixes in SCRAPER_CONSTANT_PREFIXES.items():
        module = importlib.import_module(module_path)
        for name, value in vars(module).items():
            if not name.isupper():
                continue
            if name.endswith(suffixes):
                assert name.startswith(
                    prefixes,
                ), f"{module_path}.{name} must start with one of {prefixes}"
                assert isinstance(
                    value,
                    str,
                ), f"{module_path}.{name} should be a string value"
