# Third Party
from textual.app import ComposeResult
from textual.containers import Grid, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class QuitScreen(ModalScreen[bool]):
    """Screen with a dialog to quit."""

    BINDINGS = [("escape", "app.pop_screen", "Cancel")]
    AUTO_FOCUS = "#quit"

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="dialog"):
            with Vertical(id="dialog-contents"):
                yield Label("Are you sure you want to quit?", id="question")

                with Grid(id="dialog-buttons"):
                    yield Button("Quit", variant="error", id="quit")
                    yield Button("Cancel", variant="primary", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.dismiss(True)
        else:
            self.dismiss(False)
