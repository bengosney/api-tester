# Standard Library
from datetime import datetime

# Third Party
import aiohttp
from rich.console import RenderableType
from textual.app import App, ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, Pretty, Static, TextLog, Tree

# First Party
from auth import auth
from config import api_config
from utils import extract, join_url


class Endpoint(Static):
    def __init__(
        self,
        url: str,
        renderable: RenderableType = "",
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            renderable, expand=expand, shrink=shrink, markup=markup, name=name, id=id, classes=classes, disabled=disabled
        )
        self._url = url

    @property
    def url(self) -> str:
        return join_url(api_config.settings.base_url, self._url)

    def compose(self) -> ComposeResult:
        yield Label("endpoint")
        yield Label(f"URL: {self.url}")
        yield Button("GET", id="get-url")
        with VerticalScroll():
            yield Pretty(None, id="get-response")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "get-url":
                await self.get_url()

    async def get_url(self):
        headers = {"accept": "application/json"}
        try:
            headers["Authorization"] = f"Bearer {auth['token']}"
        except KeyError:
            pass

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(self.url) as response:
                json = await response.json()
                if type(output := self.query_one("#get-response")) == Pretty:
                    output.update(json)


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
                post_data = {
                    "username": self.username_input.value,
                    "password": self.password_input.value,
                }
                async with session.post(api_config["auth"], data={**post_data}) as response:
                    json = await response.json()
                    auth["token"] = extract(json, api_config.auth.token_path)

        self.app.pop_screen()


class APITester(App):
    """Small, Simple API Tester."""

    CSS_PATH = "styles/main.css"

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("l", "toggle_debug", "Toggle debug log"),
    ]

    show_debug = False

    def compose(self) -> ComposeResult:
        tree: Tree[dict] = Tree("URLs")
        for key, val in api_config.urls.items():
            if isinstance(val, str):
                tree.root.add_leaf(f"{key} - {val}", data={"url": val})
            else:
                child = tree.root.add(key)
                for sub_key, sub_val in val.items():
                    child.add_leaf(f"{sub_key} - {sub_val}", data={"url": sub_val})

        tree.root.expand_all()

        yield Header()

        with Vertical():
            with Horizontal(id="main-pane"):
                with Container(id="left-pane"):
                    if api_config.auth_url:
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
                self.push_screen(LoginScreen())
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
