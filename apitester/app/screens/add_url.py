# Standard Library
from typing import get_args

# Third Party
from pydantic import BaseModel
from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Select

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
        self.inputs = {
            "name": Input(id="name"),
            "url": Input(id="url"),
            "method": Select(
                [(m, m) for m in get_args(URLMethod)], allow_blank=False, value=get_args(URLMethod)[0], id="method"
            ),
        }

        with Grid(id="dialog"):
            yield Form(NewURL, show_submit=False, id="url_form")
            with Grid(id="dialog-buttons"):
                yield Button("Add", variant="primary", id="add_url")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add_url":
            if type(form := self.query_one("#url_form")) == Form:
                if url := form.submit():
                    config.add_url(url.name, url.url, url.method)
                    self.dismiss(True)
        else:
            self.dismiss(False)
