import importlib

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_PATH = ROOT / "scrapers/family_contracts.py"


def load_family_contracts_module():
    spec = importlib.util.spec_from_file_location(
        "scrapers.family_contracts",
        CONTRACTS_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module
