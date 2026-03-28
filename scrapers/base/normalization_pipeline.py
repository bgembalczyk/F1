from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.links import normalize_single_link
from scrapers.base.helpers.text import strip_marks as strip_wiki_marks
from scrapers.base.normalization_utils import EmptyValuePolicy
from scrapers.base.normalization_utils import normalize_empty

LINK_KEYS = {"text", "url"}

if TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Sequence


class NormalizationPlugin(Protocol):
    def __call__(self, value: Any) -> Any: ...


def is_link_record(value: dict[str, Any]) -> bool:
    if not value:
        return False
    keys = set(value.keys())
    if not keys.issubset(LINK_KEYS):
        return False
    return bool(keys & LINK_KEYS)


def is_link_list(value: Iterable[Any]) -> bool:
    return all(isinstance(item, dict) and is_link_record(item) for item in value)


class ValueNormalizationPipeline:
    """Shared value-normalization pipeline used by base and domains.

    Deterministic order:
    1. Link structures (dict/list of links)
    2. Plain text cleanup
    3. Empty-value normalization
    4. Optional domain plugins
    """

    def __init__(
        self,
        *,
        strip_marks: bool = False,
        drop_empty: bool = True,
        strip_lang_suffix: bool = True,
        drop_empty_text: bool = False,
        empty_value_policy: EmptyValuePolicy = EmptyValuePolicy.NORMALIZE,
        plugins: Sequence[NormalizationPlugin] | None = None,
    ) -> None:
        self.strip_marks = strip_marks
        self.drop_empty = drop_empty
        self.strip_lang_suffix = strip_lang_suffix
        self.drop_empty_text = drop_empty_text
        self.empty_value_policy = empty_value_policy
        self.plugins = list(plugins or [])

    def normalize(self, value: Any) -> Any:
        result = self._normalize_links(value)
        result = self._normalize_text(result)
        result = self._normalize_empty(result)
        for plugin in self.plugins:
            result = plugin(result)
        return result

    def _normalize_links(self, value: Any) -> Any:
        if isinstance(value, dict) and is_link_record(value):
            normalized = normalize_single_link(
                value,
                strip_marks_text=self.strip_marks,
                drop_empty=self.drop_empty,
                strip_lang_suffix=self.strip_lang_suffix,
            )
            if self.drop_empty_text and normalized is not None:
                if not (normalized.get("text") or "").strip():
                    return None
            return normalized
        if isinstance(value, list) and is_link_list(value):
            normalized = normalize_links(
                value,
                strip_marks=self.strip_marks,
                drop_empty=self.drop_empty,
                strip_lang_suffix=self.strip_lang_suffix,
            )
            if self.drop_empty and not normalized:
                return None
            return normalized
        return value

    def _normalize_text(self, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        return strip_wiki_marks(value) if self.strip_marks else value

    def _normalize_empty(self, value: Any) -> Any:
        policy = self.empty_value_policy
        if self.drop_empty:
            policy = EmptyValuePolicy.NORMALIZE
        normalized = normalize_empty(value, policy=policy)
        if self.drop_empty and isinstance(normalized, str) and not normalized.strip():
            return None
        return normalized


def normalize_value(
    value: Any,
    *,
    strip_marks: bool = False,
    drop_empty: bool = True,
    strip_lang_suffix: bool = True,
    drop_empty_text: bool = False,
    empty_value_policy: EmptyValuePolicy = EmptyValuePolicy.NORMALIZE,
    plugins: Sequence[NormalizationPlugin] | None = None,
) -> Any:
    pipeline = ValueNormalizationPipeline(
        strip_marks=strip_marks,
        drop_empty=drop_empty,
        strip_lang_suffix=strip_lang_suffix,
        drop_empty_text=drop_empty_text,
        empty_value_policy=empty_value_policy,
        plugins=plugins,
    )
    return pipeline.normalize(value)
