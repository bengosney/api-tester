# Third Party
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Label

# First Party
from apitester.plugin_manager import PluginManager


class PluginScreen(ModalScreen[None]):
    """Screen with a dialog to quit."""

    BINDINGS = [("escape", "dismiss", "Cancel")]
    AUTO_FOCUS = "Button"

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="dialog"):
            yield Label("Active Plugins", classes="title")
            yield DataTable(id="plugin-list")
            yield Button("Close", id="close")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)

        table.add_columns("Name", "Description")

        plugins = getattr(self.app, "plugin_manager", PluginManager(self.log))

        for name, description in plugins.active_plugins:
            self.log(f"plugin {name} - {description}")
            table.add_row(name, description)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()
