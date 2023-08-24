# Standard Library
import inspect
from typing import Any, Literal, TypeVar

# Third Party
from pydantic import BaseModel
from textual.app import ComposeResult
from textual.containers import Grid, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button

# First Party
from apitester.widgets import Form

ScreenResultType = TypeVar("ScreenResultType", bound=BaseModel)


class ModalFormException(Exception):
    pass


class ModalFormScreen(ModalScreen[ScreenResultType | Literal[False]]):
    BINDINGS = [("escape", "dismiss", "Cancel")]

    model: type[ScreenResultType]
    error_message: str | None = None
    _inital: dict[str, Any]

    def __init__(
        self, model: type[ScreenResultType] | None = None, inital: dict[str, Any] | None = None, *args, **kwargs
    ) -> None:
        if model is not None:
            self.model = model

        self._inital = inital or {}

        super().__init__(*args, **kwargs)

    @property
    def inital(self) -> dict[str, Any]:
        return self._inital

    def compose(self) -> ComposeResult:
        self.form = Form[ScreenResultType](self.model, show_submit=False, id="url_form", inital=self.inital)

        with VerticalScroll(id="dialog"):
            yield self.form
            with Grid(id="dialog-buttons"):
                yield Button("Add", variant="primary", id="submit")
                yield Button("Cancel", id="cancel")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            if model := self.form.submit():
                try:
                    result = self.on_submit(model)
                    if inspect.isawaitable(result):
                        await result
                    self.dismiss(model)
                except ModalFormException as e:
                    self.error_message = str(e)
        else:
            self.dismiss(False)

    async def on_submit(self, model: ScreenResultType) -> None:
        pass
