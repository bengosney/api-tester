# Standard Library
from datetime import datetime

# Third Party
import aiohttp
from textual.app import App, ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, TextLog, Tree

# First Party
from apitester.auth import auth
from apitester.config import BearerAuthConf, api_config
from apitester.url import URL
from apitester.utils import extract
from apitester.widgets import Endpoint


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


class LoginScreen(Screen):
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
        ("l", "toggle_debug", "Toggle debug log"),
    ]

    show_debug = False

    def compose(self) -> ComposeResult:
        tree: Tree[dict] = Tree("URLs")

        def build_tree(items: dict, node):
            for key, val in items.items():
                if isinstance(val, dict):
                    build_tree(val, node.add(key))
                elif isinstance(val, str):
                    node.add_leaf(f"{key} - {val}", data={"url": URL(val)})
                else:
                    node.add_leaf(f"{key} - {val.url}", data={"url": val})

        build_tree(api_config.urls, tree.root)

        tree.root.expand_all()

        yield Header()

        with Vertical():
            with Horizontal(id="main-pane"):
                with Container(id="left-pane"):
                    if api_config.auth.type != "none":
                        yield Button("Auth", id="auth")
                    yield Label("URL List")
                    with VerticalScroll():
                        yield tree
                with Container():
                    with VerticalScroll():
                        yield Container(id="query-container")

            with Grid(id="debug-log-wrapper"):
                with Container(id="debug-log-buttons"):
                    yield TextLog(id="debug-log")
                yield Button("Clear log", id="clear-debug")
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_toggle_debug(self) -> None:
        self.show_debug = not self.show_debug
        self.query_one("#debug-log-wrapper").styles.display = "block" if self.show_debug else "none"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "auth":
                if api_config.auth.type == "bearer":
                    self.push_screen(LoginScreen(api_config.auth))
                if api_config.auth.type == "header":
                    self.push_screen(APIKeyScreen())
            case "clear-debug":
                self.debug_log_clear()

    def debug_log_clear(self) -> None:
        textlog = self.query_one("#debug-log")
        if type(textlog) == TextLog:
            textlog.clear()

    def debug_log(self, msg: str, context=None) -> None:
        textlog = self.query_one("#debug-log")
        if type(textlog) == TextLog:
            now = datetime.now()
            textlog.write(f'{now.strftime("%H:%M.%S")}: {msg}')
            if context:
                textlog.write(context)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if event.node.data:
            self.debug_log(f'selected {event.node.data["url"]}', event.node.__dict__)
            qc = self.query_one("#query-container")
            qc.remove_children()
            qc.mount(Endpoint(event.node.data["url"]))
        else:
            self.debug_log("node has no url?")


if __name__ == "__main__":
    app = APITester()
    print(app.run())
