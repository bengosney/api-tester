# Third Party
from pydantic import BaseModel
from textual.app import ComposeResult
from textual.validation import Length, Number, Validator
from textual.widget import Widget
from textual.widgets import Input, Label, Select, Switch


class Form(Widget):
    model: type[BaseModel]

    def __init__(self, model: type[BaseModel], *args, **kwargs) -> None:
        self.model = model
        super().__init__(*args, **kwargs)

    def on_mount(self) -> None:
        self.styles.padding = 2

    def compose(self) -> ComposeResult:
        schema = self.model.model_json_schema()
        for id, field in schema["properties"].items():
            required = id in schema["required"]
            postfix = "*" if required else ""
            id = f"{id}_input"

            if "enum" in field:
                field["type"] = "enum"

            yield Label(f"{field['title']}{postfix}")
            match field.get("type", "any"):
                case "boolean":
                    yield Switch(id=id, value=field.get("default", False))
                case "enum":
                    yield Select(
                        zip(map(str, field["enum"]), field["enum"]),
                        id=id,
                        allow_blank=(not required),
                        value=field.get("default", ""),
                    )
                case _:
                    validators: list[Validator] = []
                    if required:
                        validators.append(Length(1))
                    if field.get("type", "") == "integer":
                        validators.append(Number())

                    yield Input(id=id, validators=validators, value=field.get("default", ""))
