from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Footer, Header, Static, Tree, Label, Button

from config import api_config


class APITester(App):
    """Small, Simple API Tester."""

    CSS_PATH = "styles/main.css"

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        tree: Tree[dict] = Tree("URLs")
        for key, val in api_config.urls.items():
            if isinstance(val, str):
                tree.root.add_leaf(f"{key} - {val}")
            else:
                child = tree.root.add(key)
                for sub_key, sub_val in val.items():
                    child.add_leaf(f"{sub_key} - {sub_val}")

        tree.root.expand_all()

        yield Header()
        with Horizontal():
            with Container(id="left-pane"):
                yield Button("Auth", id="auth")
                yield Label("URL List")
                with VerticalScroll():
                    yield tree
            with Container():
                with VerticalScroll():
                    yield Static("query")

        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.exit(str(event.button))


if __name__ == "__main__":
    app = APITester()
    print(app.run())
