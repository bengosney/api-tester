# Standard Library
from contextlib import suppress
from typing import Generic, Literal, TypeVar

# Third Party
from pydantic import BaseModel, ValidationError
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.css.query import QueryError
from textual.message import Message
from textual.validation import Integer, Length, Number
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Select, Switch

T = TypeVar("T", bound=BaseModel)


class Form(Widget, Generic[T]):
    model: type[T]
    show_submit: bool

    class Submit(Message):
        def __init__(self, model: T) -> None:
            self.model = model
            super().__init__()

    def __init__(self, model: type[T], show_submit: bool = True, classes: str | None = None, *args, **kwargs) -> None:
        self.model = model
        self._schema = model.model_json_schema()
        self.show_submit = show_submit
        super().__init__(classes=classes or "form", *args, **kwargs)

    def on_mount(self) -> None:
        self.styles.padding = 2

    def compose(self) -> ComposeResult:
        schema = self._schema
        yield Label(schema["title"], classes="title")

        for id, field in schema["properties"].items():
            _id = f"{id}_input"

            if "enum" in field:
                field["type"] = "enum"

            field_types = set()
            with suppress(KeyError):
                field_types.add(field["type"])

            for _type in field.get("anyOf", []):
                with suppress(KeyError):
                    field_types.add(_type["type"])

            required = None not in field_types
            field_types = list(filter(lambda i: i is not None, field_types))

            default = str(field.get("default", ""))
            placeholder = "" if default == "" else f"Default: {default}"

            _widget = None
            match field_types:
                case ["boolean"]:
                    _widget = Switch(id=_id, value=field.get("default", False))
                case ["enum"]:
                    _widget = Select(
                        zip(map(str, field["enum"]), field["enum"]),
                        id=_id,
                        allow_blank=(not required),
                        value=default,
                    )
                case ["string", "null"]:
                    required = False
                    _widget = Input(id=_id, validators=[], value=default, placeholder=placeholder)
                case ["string"]:
                    _widget = Input(id=_id, validators=[Length(int(required))], value=default, placeholder=placeholder)
                case ["integer"]:
                    _widget = Input(
                        id=_id, validators=[Integer(), Length(int(required))], value=default, placeholder=placeholder
                    )
                case ["number"]:
                    _widget = Input(
                        id=_id, validators=[Number(), Length(int(required))], value=default, placeholder=placeholder
                    )
                case [unmatched]:
                    raise Exception(f"Unmatched: {unmatched}")

            if _widget:
                with Container(classes="input-wrapper"):
                    with Horizontal():
                        yield Label(f"{field['title']}{'*' if required else ''}", classes="input-label")
                        yield Label("", id=f"{_id}_error", classes="error")
                    yield _widget

        if self.show_submit:
            yield Button("submit", id="submit")

    def submit(self) -> T | Literal[False]:
        schema = self._schema
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
            return model
        except ValidationError as e:
            for error in e.errors():
                for id in error["loc"]:
                    with suppress(QueryError):
                        if input := self.query_one(f"#{id}_input"):
                            input.set_class(True, "-invalid")

                    with suppress(QueryError):
                        if type(label := self.query_one(f"#{id}_input_error")) == Label:
                            label.update(error["msg"])

        return False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            if model := self.submit():
                self.post_message(self.Submit(model))
