from typing import Any
from typing import Dict

from scrapers.base.table.columns.context import ColumnContext


def restart_status(ctx: ColumnContext) -> Dict[str, Any] | None:
    text = (ctx.clean_text or "").strip()
    if not text:
        return None
    code = text[0].upper()
    mapping = {
        "N": "race_was_not_restarted",
        "Y": "race_was_restarted_over_original_distance",
        "R": "race_was_resumed_to_complete_original_distance",
        "S": "race_was_restarted_or_resumed_without_completing_original_distance",
    }
    return {"code": code, "description": mapping.get(code)}
