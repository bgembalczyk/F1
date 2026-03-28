from __future__ import annotations

from enum import StrEnum


class TransformerStage(StrEnum):
    PRE_VALIDATE = "pre-validate"
    ENRICH = "enrich"
    POST_VALIDATE = "post-validate"

