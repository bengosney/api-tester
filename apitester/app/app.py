# Standard Library

# Third Party
import aiohttp
from textual.app import App, ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, Tree

# First Party
from apitester.auth import auth
from apitester.config import BearerAuthConf, config
from apitester.utils import extract
from apitester.widgets import Endpoint, URLTree


class APIKeyScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

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


class LoginScreen(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def __init__(self, auth: BearerAuthConf, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.auth = auth

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
                post_data = {
                    "username": self.username_input.value,
                    "password": self.password_input.value,
                }
                async with session.post(self.auth.url, data={**post_data}) as response:
                    json = await response.json()
                    auth["token"] = extract(json, self.auth.token_path)

        self.app.pop_screen()


class APITester(App):
    """Small, Simple API Tester."""

    CSS_PATH = "../styles/main.css"

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("r", "reload_config", "Reload Config"),
    ]

    def compose(self) -> ComposeResult:
        tree: URLTree = URLTree(config.urls)

        yield Header()

        with Vertical():
            with Horizontal(id="main-pane"):
                with Container(id="left-pane"):
                    if config.auth.type != "none":
                        yield Button("Auth", id="auth")
                    yield Label("URL List")
                    with VerticalScroll():
                        yield tree
                with Container():
                    with VerticalScroll():
                        yield Container(id="query-container")

        yield Footer()

    def action_reload_config(self) -> None:
        if config.check_reload():
            self.query_one(URLTree).update(config.urls)

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "auth":
                if config.auth.type == "bearer":
                    self.push_screen(LoginScreen(config.auth))
                if config.auth.type == "header":
                    self.push_screen(APIKeyScreen())

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if event.node.data:
            qc = self.query_one("#query-container")
            qc.remove_children()
            qc.mount(Endpoint(event.node.data["url"]))


if __name__ == "__main__":
    app = APITester()
    print(app.run())
