# Standard Library

# Third Party
from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Input, Label

# First Party
from apitester.auth import auth


class APIKeyScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Cancel")]

    def compose(self) -> ComposeResult:
        self.api_key_input = Input(id="username", value=auth.get("api_key"))
        self.remember = Checkbox(id="remember", value=True)

        with Grid(id="dialog"):
            with Grid(id="dialog-inputs"):
                yield Label("Add API Key", id="question")
                yield Label("")
                yield self.api_key_input
                yield Label("Remember API Key")
                yield self.remember
            with Grid(id="dialog-buttons"):
                yield Button("Auth", variant="primary", id="do_auth")
                yield Button("Cancel", id="cancel")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "do_auth":
            if self.remember.value:
                auth.store("api_key", self.api_key_input.value)
            else:
                auth.remove()

            auth["api_key"] = self.api_key_input.value
        self.app.pop_screen()
