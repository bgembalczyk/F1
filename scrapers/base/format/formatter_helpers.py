from typing import Any, Dict, List

from models.mappers.serialization import to_dict_list
from scrapers.base.results import ScrapeResult


def extract_data(result: ScrapeResult) -> List[Dict[str, Any]]:
    """
    Główna, spójna ścieżka ekstrakcji danych:
    - zawsze zwracamy list[dict[str,Any]]
    - wykorzystujemy to_dict_list (Twoja wspólna warstwa serializacji)
    """
    return to_dict_list(list(result.data))
