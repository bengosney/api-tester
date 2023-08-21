# Third Party
from pydantic import BaseModel, ValidationError
from textual.app import ComposeResult
from textual.containers import Container
from textual.validation import Length, Number
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Select, Switch


class Form(Widget):
    model: type[BaseModel]

    def __init__(self, model: type[BaseModel], *args, **kwargs) -> None:
        self.model = model
        super().__init__(*args, **kwargs)

    def on_mount(self) -> None:
        self.styles.padding = 2

    def compose(self) -> ComposeResult:
        schema = self.model.model_json_schema()
        yield Label(schema["title"])

        for id, field in schema["properties"].items():
            required = id in schema["required"]
            _id = f"{id}_input"

            if "enum" in field:
                field["type"] = "enum"

            field_types = []
            field_types.append(field.get("type", None))
            for _type in field.get("anyOf", []):
                field_types.append(_type.get("type", None))
            field_types = list(filter(lambda i: i is not None, field_types))

            _widget = None
            match field_types:
                case ["boolean"]:
                    _widget = Switch(id=_id, value=field.get("default", False))
                case ["enum"]:
                    _widget = Select(
                        zip(map(str, field["enum"]), field["enum"]),
                        id=_id,
                        allow_blank=(not required),
                        value=field.get("default", ""),
                    )
                case ["string", "null"]:
                    required = False
                    _widget = Input(id=_id, validators=[], value=field.get("default", ""))
                case ["string"]:
                    _widget = Input(id=_id, validators=[Length(1 if required else 0)], value=field.get("default", ""))
                case ["integer"]:
                    _widget = Input(id=_id, validators=[Number(), Length(1 if required else 0)], value=field.get("default", ""))
                case [unmatched]:
                    raise Exception(f"Unmatched: {unmatched}")

            if _widget:
                with Container(classes="input-wrapper"):
                    yield Label(f"{field['title']}{'*' if required else ''}")
                    yield Label("", id=f"{_id}_error", classes="error")
                    yield _widget

        yield Button("submit", id="submit")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            schema = self.model.model_json_schema()
            data = {}
            for id, _ in schema["properties"].items():
                if input := self.query_one(f"#{id}_input"):
                    input.set_class(False, "-invalid")

                if val := getattr(input or None, "value", None):
                    data[id] = val
                else:
                    data[id] = None

                if type(label := self.query_one(f"#{id}_input_error")) == Label:
                    label.update("")

            try:
                model = self.model(**data)
                self.log(model)
            except ValidationError as e:
                for error in e.errors():
                    self.log(error)
                    for id in error["loc"]:
                        if input := self.query_one(f"#{id}_input"):
                            input.set_class(True, "-invalid")

                        if type(label := self.query_one(f"#{id}_input_error")) == Label:
                            label.update(error["msg"])
