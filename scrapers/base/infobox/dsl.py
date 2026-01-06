from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from scrapers.base.infobox.schema import InfoboxSchema, InfoboxSchemaField


@dataclass(frozen=True)
class InfoboxFieldSpec:
    key: str
    labels: Iterable[str]
    parser: str | None = None

    def build(self) -> InfoboxSchemaField:
        return InfoboxSchemaField(
            key=self.key,
            labels=tuple(self.labels),
            parser=self.parser,
        )


def field(
    key: str,
    labels: Iterable[str],
    *,
    parser: str | None = None,
) -> InfoboxFieldSpec:
    return InfoboxFieldSpec(key=key, labels=labels, parser=parser)


@dataclass(frozen=True)
class InfoboxSchemaDSL:
    fields: Iterable[InfoboxFieldSpec]
    name: str | None = None
    required_keys: Iterable[str] | None = None
    normalize_unknown: bool = True

    def build(self) -> InfoboxSchema:
        return InfoboxSchema(
            fields=[field.build() for field in self.fields],
            name=self.name,
            required_keys=self.required_keys,
            normalize_unknown=self.normalize_unknown,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "required_keys": list(self.required_keys) if self.required_keys else None,
            "normalize_unknown": self.normalize_unknown,
            "fields": [
                {
                    "key": field.key,
                    "labels": list(field.labels),
                    "parser": field.parser,
                }
                for field in self.fields
            ],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "InfoboxSchemaDSL":
        fields_data = data.get("fields", [])
        return cls(
            name=data.get("name"),
            required_keys=data.get("required_keys"),
            normalize_unknown=data.get("normalize_unknown", True),
            fields=[
                InfoboxFieldSpec(
                    key=item["key"],
                    labels=item.get("labels", []),
                    parser=item.get("parser"),
                )
                for item in fields_data
            ],
        )

    @classmethod
    def from_schema(cls, schema: InfoboxSchema) -> "InfoboxSchemaDSL":
        return cls(
            name=schema.name,
            required_keys=list(schema.required_keys),
            normalize_unknown=schema.normalize_unknown,
            fields=[
                InfoboxFieldSpec(
                    key=field.key,
                    labels=field.labels,
                    parser=field.parser if isinstance(field.parser, str) else None,
                )
                for field in schema.fields
            ],
        )
