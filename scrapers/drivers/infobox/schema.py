from scrapers.base.infobox.schema import InfoboxSchema, InfoboxSchemaField

DRIVER_GENERAL_SCHEMA = InfoboxSchema(
    name="driver.general",
    fields=[
        InfoboxSchemaField(key="born", labels=("Born",), parser="date_place"),
        InfoboxSchemaField(key="died", labels=("Died",), parser="date_place"),
        InfoboxSchemaField(
            key="parents",
            labels=("Parent", "Parents", "Parent(s)"),
            parser="relations",
        ),
        InfoboxSchemaField(key="relatives", labels=("Relatives",), parser="relations"),
        InfoboxSchemaField(key="children", labels=("Children",), parser="links"),
        InfoboxSchemaField(
            key="cause_of_death", labels=("Cause of death",), parser="text"
        ),
    ],
)
