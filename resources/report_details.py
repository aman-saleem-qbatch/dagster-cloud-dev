from dagster import resource, Field, String


@resource(config_schema={"id": Field(String)})
def get_details(context):
    return {"data": context.resource_config["id"]}
