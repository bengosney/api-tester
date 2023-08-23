# Third Party
from pydantic import BaseModel
from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button

# First Party
from apitester.auth import auth
from apitester.widgets import Form


class APIKey(BaseModel):
    api_key: str
    remember: bool = True


class APIKeyScreen(ModalScreen[bool]):
    BINDINGS = [("escape", "app.pop_screen", "Cancel")]

    def compose(self) -> ComposeResult:
        self.form = Form[APIKey](APIKey, show_submit=False, id="api_key_form")
        with Grid(id="dialog"):
            yield self.form
            with Grid(id="dialog-buttons"):
                yield Button("Auth", variant="primary", id="do_auth")
                yield Button("Cancel", id="cancel")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "do_auth":
            if api_key := self.form.submit():
                if api_key.remember:
                    auth.store("api_key", api_key.api_key)
                else:
                    auth.remove()
                auth["api_key"] = api_key.api_key
                self.dismiss(True)
        else:
            self.dismiss(False)
