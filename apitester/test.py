# Third Party
from devtools import debug

# First Party
from apitester.app.app import User

schema = User.model_json_schema()
debug(schema)

for id, field in schema["properties"].items():
    field_types = []
    field_types.append(field.get("type", None))
    for _type in field.get("anyOf", []):
        field_types.append(_type.get("type", None))
    field_types = filter(lambda i: i is not None, field_types)
    debug(field_types)
