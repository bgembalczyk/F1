class TableRecordMapper:
    """Maps table rows to normalized dictionaries.

    Normalization rules:
    - row payload must be mapping,
    - key names are stringified and stripped,
    - nested mapping/list values are normalized recursively.
    """

    def map(self, payload: TableRecordInput | Mapping[str, Any]) -> dict[str, Any]:
        source = payload.payload if isinstance(payload, TableRecordInput) else payload
        if not isinstance(source, Mapping):
            msg = "Table mapper contract violation: payload must be mapping."
            raise TypeError(msg)
        return {
            str(key).strip(): self._normalize_value(value)
            for key, value in source.items()
        }

    def map_many(self, payloads: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        return [self.map(payload) for payload in payloads]

    def _normalize_value(self, value: Any) -> Any:
        if isinstance(value, Mapping):
            return {str(k).strip(): self._normalize_value(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._normalize_value(item) for item in value]
        return value

