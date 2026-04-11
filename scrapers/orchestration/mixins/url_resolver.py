from typing import Any


class UrlResolverMixin:
    KEY_MAP: dict[str, str] = {
        "drivers": "driver",
        "constructors": "constructor",
        "circuits": "circuit",
        "seasons": "season",
        "grands_prix": "grand_prix",
    }

    def resolve_url_row(self, domain: str, row: dict[str, Any]) -> dict[str, Any]:
        if "url" in row:
            return {"name": str(row.get("name", "")), "url": str(row.get("url", ""))}

        nested_key = self.KEY_MAP.get(domain, "")
        nested = row.get(nested_key)
        if isinstance(nested, dict):
            return {
                "name": str(nested.get("text", "")),
                "url": str(nested.get("url", "")),
            }
        return {"name": "", "url": ""}
