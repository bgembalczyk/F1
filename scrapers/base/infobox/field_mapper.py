from typing import Any
from typing import Dict

from scrapers.base.infobox.schema import InfoboxSchema


class InfoboxFieldMapper:
    """Mapuje surowe pola infoboxa do docelowego formatu."""

    def __init__(
            self,
            *,
            schema: InfoboxSchema | None = None,
            logger=None,
            context: str | None = None,
    ) -> None:
        self._schema = schema
        self._logger = logger
        self._context = context

    def map(self, raw: Dict[str, Any] | None) -> Dict[str, Any]:
        if not raw:
            return {"title": None, "rows": {}}

        data = dict(raw)
        data.setdefault("title", None)
        rows = data.get("rows") or {}

        if isinstance(rows, dict):
            if self._schema is not None:
                rows = self._schema.normalize_rows(
                    rows,
                    logger=self._logger,
                    context=self._context,
                )
                self._schema.log_missing(
                    rows.keys(),
                    logger=self._logger,
                    context=self._context,
                )
        else:
            rows = {}

        data["rows"] = rows
        return data
