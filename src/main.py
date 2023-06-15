from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll, Grid
from textual.widgets import Footer, Header, Static, Tree, Label, Button, Input
from textual.screen import Screen

import aiohttp
import keyring


from config import api_config

class LoginScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        yield Grid(
            Label('Get Auth Token', id="question"),
            Label('Username'),
            Input(id="username"),
            Label('Password'),
            Input(id="password", password=True),
            Button('Auth', variant="primary", id="do_auth"),
            Button('Cancel', id="cancel"),
            id="dialog"
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_config['auth']) as response:
                    html = await response.text()
                    self.app.exit(html)
            

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
                if api_config.auth_url:
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
        if event.button.id == 'auth':
            self.push_screen(LoginScreen())


if __name__ == "__main__":
    app = APITester()
    print(app.run())
