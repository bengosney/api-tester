# Standard Library

# Third Party
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Footer, Header, Label, Tree

# First Party
from apitester.app.screens import AddURLScreen, APIKeyScreen, LoginScreen, QuitScreen
from apitester.config import config
from apitester.widgets import Endpoint, URLTree


class APITester(App):
    """Small, Simple API Tester."""

    CSS_PATH = "../styles/main.css"

    BINDINGS = [
        ("q", "try_quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
        ("r", "reload_config", "Reload Config"),
        ("n", "add_url", "Add a new url"),
        ("a", "auth", "Authenticate"),
    ]

    def compose(self) -> ComposeResult:
        tree: URLTree = URLTree(config.urls)

        yield Header()

        with Vertical():
            with Horizontal(id="main-pane"):
                with Container(id="left-pane"):
                    if config.auth.type != "none":
                        yield Button("Authenticate", id="auth")
                    yield Label("URL List")
                    with VerticalScroll():
                        yield tree
                with Container():
                    with VerticalScroll():
                        with Container(id="query-container"):
                            pass

        yield Footer()

    def action_reload_config(self) -> None:
        if config.check_reload():
            self._reload()
            self.notify("Reloaded OK", title="Reload Config")
        else:
            self.notify("No changes", title="Reload Config")

    def _reload(self) -> None:
        if tree := self.query_one(URLTree):
            tree.update(config.urls)

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def auth(self):
        match config.auth.type:
            case "bearer":
                self.push_screen(LoginScreen(config.auth))
            case "header":
                self.push_screen(APIKeyScreen())

    def action_auth(self):
        self.auth()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "auth":
                self.auth()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if event.node.data:
            qc = self.query_one("#query-container")
            qc.remove_children()
            qc.mount(Endpoint(event.node.data["url"]))

    def action_add_url(self):
        self.push_screen(AddURLScreen(), lambda ok: self._reload() if ok else None)

    def action_try_quit(self) -> None:
        """Action to display the quit dialog."""

        def check_quit(quit: bool) -> None:
            """Called when QuitScreen is dismissed."""
            if quit:
                self.exit()

        self.push_screen(QuitScreen(), check_quit)


if __name__ == "__main__":
    app = APITester()
    print(app.run())
