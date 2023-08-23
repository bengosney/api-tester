# Third Party
from pydantic import BaseModel
from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button

# First Party
from apitester.config import config
from apitester.types import URLMethod
from apitester.widgets import Form


class NewURL(BaseModel):
    name: str
    url: str
    method: URLMethod = "GET"


class AddURLScreen(ModalScreen[bool]):
    BINDINGS = [("escape", "app.pop_screen", "Cancel")]

    def compose(self) -> ComposeResult:
        self.form = Form[NewURL](NewURL, show_submit=False, id="url_form")

        with Grid(id="dialog"):
            yield self.form
            with Grid(id="dialog-buttons"):
                yield Button("Add", variant="primary", id="add_url")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add_url":
            if url := self.form.submit():
                config.add_url(**dict(url))
                self.dismiss(True)
        else:
            self.dismiss(False)
