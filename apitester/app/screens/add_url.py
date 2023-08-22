# Standard Library
from typing import get_args

# Third Party
from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select

# First Party
from apitester.config import config
from apitester.types import URLMethod


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
            with Grid(id="dialog-inputs"):
                yield Label("Add new URL", id="question")
                yield Label("Name")
                yield self.inputs["name"]
                yield Label("URL")
                yield self.inputs["url"]
                yield Label("Method")
                yield self.inputs["method"]
            with Grid(id="dialog-buttons"):
                yield Button("Add", variant="primary", id="add_url")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add_url":
            name = self.inputs["name"].value
            url = self.inputs["url"].value
            method = self.inputs["method"].value

            if all([i is not None for i in [name, url, method]]) and method in get_args(URLMethod):
                config.add_url(name, url, method)
                self.dismiss(True)
        else:
            self.dismiss(False)
