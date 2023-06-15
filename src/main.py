# Third Party
import aiohttp
from textual.app import App, ComposeResult
from textual.containers import Container, Grid, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, Static, Tree

# First Party
from auth import auth
from config import api_config


class LoginScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        self.username_input = Input(id="username", value=auth.username)
        self.password_input = Input(id="password", password=True, value=auth.password)
        self.remember = Checkbox(id="remember", value=True)

        with Grid(id="dialog"):
            with Grid(id="dialog-inputs"):
                yield Label("Get Auth Token", id="question")
                yield Label("Username")
                yield self.username_input
                yield Label("Password")
                yield self.password_input
                yield Label("Remember me")
                yield self.remember
            with Grid(id="dialog-buttons"):
                yield Button("Auth", variant="primary", id="do_auth")
                yield Button("Cancel", id="cancel")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "do_auth":
            if self.remember.value:
                auth.store(self.username_input.value, self.password_input.value)
            else:
                auth.remove()

            async with aiohttp.ClientSession() as session:
                async with session.get(api_config["auth"]) as response:
                    json = await response.json()
                    self.app.exit(json)

        self.app.pop_screen()


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
        if event.button.id == "auth":
            self.push_screen(LoginScreen())


if __name__ == "__main__":
    app = APITester()
    print(app.run())
