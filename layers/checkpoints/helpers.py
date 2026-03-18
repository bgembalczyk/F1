from typing import Any


def _extract_driver_seed_row(row: dict[str, Any]) -> tuple[str, str] | None:
    driver_field = row.get("driver")
    if not isinstance(driver_field, dict):
        return None
    url = driver_field.get("url")
    if not isinstance(url, str) or not url:
        return None
    text = driver_field.get("text")
    name = text if isinstance(text, str) else ""
    return name, url


def _filter_checkpoint_urls(records: list[dict[str, Any]]) -> list[str]:
    checkpoint_urls = [record.get("url") for record in records]
    return [url for url in checkpoint_urls if isinstance(url, str) and url]

