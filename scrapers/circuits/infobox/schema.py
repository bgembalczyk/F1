from scrapers.base.infobox.schema import InfoboxSchema, InfoboxSchemaField

CIRCUIT_INFOBOX_SCHEMA = InfoboxSchema(
    name="circuit.infobox",
    fields=[
        InfoboxSchemaField(key="location", labels=("Location",)),
        InfoboxSchemaField(key="coordinates", labels=("Coordinates",)),
        InfoboxSchemaField(key="fia_grade", labels=("FIA Grade",)),
        InfoboxSchemaField(key="length", labels=("Length",)),
        InfoboxSchemaField(key="turns", labels=("Turns",)),
        InfoboxSchemaField(key="race_lap_record", labels=("Race lap record",)),
        InfoboxSchemaField(key="opened", labels=("Opened",)),
        InfoboxSchemaField(key="closed", labels=("Closed",)),
        InfoboxSchemaField(key="former_names", labels=("Former names",)),
        InfoboxSchemaField(key="owner", labels=("Owner",)),
        InfoboxSchemaField(key="operator", labels=("Operator",)),
        InfoboxSchemaField(key="capacity", labels=("Capacity",)),
        InfoboxSchemaField(key="broke_ground", labels=("Broke ground",)),
        InfoboxSchemaField(key="built", labels=("Built",)),
        InfoboxSchemaField(key="construction_cost", labels=("Construction cost",)),
        InfoboxSchemaField(key="website", labels=("Website",)),
        InfoboxSchemaField(key="area", labels=("Area",)),
        InfoboxSchemaField(key="major_events", labels=("Major events",)),
        InfoboxSchemaField(key="address", labels=("Address",)),
        InfoboxSchemaField(key="architect", labels=("Architect",)),
        InfoboxSchemaField(key="surface", labels=("Surface",)),
        InfoboxSchemaField(key="banking", labels=("Banking",)),
    ],
)
