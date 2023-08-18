# Standard Library
from typing import get_args

# Third Party
import aiohttp
from textual.app import App, ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, Select, Tree

# First Party
from apitester.auth import auth
from apitester.config import BearerAuthConf, config
from apitester.types import URLMethod
from apitester.utils import extract
from apitester.widgets import Endpoint, URLTree


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

        self.dismiss()


class QuitScreen(ModalScreen[bool]):
    """Screen with a dialog to quit."""

    BINDINGS = [("escape", "app.pop_screen", "Cancel")]

    def compose(self) -> ComposeResult:
        with Grid(id="dialog"):
            with Grid(id="dialog-inputs"):
                yield Label("Are you sure you want to quit?", id="question")
            with Grid(id="dialog-buttons"):
                yield Button("Quit", variant="error", id="quit")
                yield Button("Cancel", variant="primary", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.dismiss(True)
        else:
            self.dismiss(False)


class AddURLScreen(ModalScreen[bool]):
    BINDINGS = [("escape", "app.pop_screen", "Cancel")]

    def compose(self) -> ComposeResult:
        self.inputs = {
            "name": Input(id="name"),
            "url": Input(id="url"),
            "method": Select(
                [(m, m) for m in get_args(URLMethod)], allow_blank=False, value=get_args(URLMethod)[0], id="method"
            ),
        }

        with Grid(id="dialog"):
            with Grid(id="dialog-inputs"):
                yield Label("Add new URL", id="question")
                yield Label("Name")
                yield self.inputs["name"]
                yield Label("URL")
                yield self.inputs["url"]
                yield Label("Method")
                yield self.inputs["method"]
            with Grid(id="dialog-buttons"):
                yield Button("Add", variant="primary", id="add_url")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add_url":
            name = self.inputs["name"].value
            url = self.inputs["url"].value
            method = self.inputs["method"].value

            if all([i is not None for i in [name, url, method]]) and method in get_args(URLMethod):
                config.add_url(name, url, method)
                self.dismiss(True)
        else:
            self.dismiss(False)


class APITester(App):
    """Small, Simple API Tester."""

    CSS_PATH = "../styles/main.css"

    BINDINGS = [
        ("q", "try_quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
        ("r", "reload_config", "Reload Config"),
        ("a", "add_url", "Add a url"),
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
            self._reload()

    def _reload(self) -> None:
        if tree := self.query_one(URLTree):
            tree.update(config.urls)

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
