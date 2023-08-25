# Third Party
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Label

# First Party
from apitester.plugin_manager import PluginManager


class PluginScreen(ModalScreen[None]):
    """Screen with a dialog to quit."""

    BINDINGS = [("escape", "dismiss", "Cancel")]
    AUTO_FOCUS = "Button"

    def compose(self) -> ComposeResult:
        plugins = getattr(self.app, "plugin_manager", PluginManager(self.log))

        with VerticalScroll(id="dialog"):
            yield Label("Active Plugins", classes="title")
            with VerticalScroll(id="list"):
                for plugin in plugins.active_plugins:
                    yield Label(f"{plugin}")
            yield Button("Close", id="close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()
