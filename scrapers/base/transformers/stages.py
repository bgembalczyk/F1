from __future__ import annotations

from enum import Enum


class TransformerStage(str, Enum):
    PRE_VALIDATE = "pre-validate"
    ENRICH = "enrich"
    POST_VALIDATE = "post-validate"
