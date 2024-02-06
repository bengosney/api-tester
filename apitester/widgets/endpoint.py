# Standard Library
from contextlib import suppress

# Third Party
import aiohttp
from aiohttp import BasicAuth
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, Pretty, Static
from textual.worker import Worker, WorkerState

# First Party
from apitester.auth import auth
from apitester.config import config
from apitester.data import DataStore
from apitester.plugin_manager import PluginManager
from apitester.url import URL
from apitester.widgets.labels import AdvancedLabel
from apitester.widgets.loader import Loader


class Endpoint(Static):
    loadingCount: int = 0

    DEFAULT_CSS = """
    Endpoint {
        padding: 1;
    }
    """

    def __init__(self, url: URL, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.url = url
        self.store = DataStore(f"{url.url}-{url.method}")

    def on_mount(self):
        for input in self.query("Input"):
            if type(input) is Input and input.value == "":
                input.focus()
                break
        else:
            self.query_one("#get-url").focus()

    def compose(self) -> ComposeResult:
        yield AdvancedLabel(f"{self.url}", prefix="URL: ", id="url-label")
        yield Label(f"Method: {self.url.method}", id="method-label")
        yield Static(id="loader")

        if self.url.variable_count > 0:
            with VerticalScroll(id="vars-grid"):
                for field in self.url.variables():
                    id = f"{field}-input"
                    with Horizontal():
                        yield Label(field)
                        yield Input(id=id, value=self.store[id])

        with Vertical(id="output"):
            yield Button(self.url.method, id="get-url")
            with VerticalScroll():
                yield Pretty(None, id="get-response")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "get-url":
                self.get_url()

    @on(Input.Changed)
    def update_vars(self, event: Input.Changed) -> None:
        if type(self.url) is URL:
            for field in self.url.variables():
                id = f"{field}-input"
                if type(input := self.query_one(f"#{id}")) == Input:
                    self.url[field] = input.value
                    self.store[id] = input.value

            if Label in type.mro(type(label := self.query_one("#url-label"))):
                label.update(str(self.url))  # type: ignore

    @work()
    async def get_url(self):
        plugins = getattr(self.app, "plugin_manager", PluginManager(self.log))

        headers = plugins.get_headers({"accept": "application/json"})
        cookies = plugins.get_cookies()

        basic_auth = None

        with suppress(KeyError):
            match config.auth.type:
                case "bearer":
                    headers["Authorization"] = f"Bearer {auth['token']}"
                case "header":
                    headers[getattr(config.auth, "key")] = auth["api_key"]
                case "basic":
                    basic_auth = BasicAuth((auth.username or "").strip(), (auth.password or "").strip())

        if type(output := self.query_one("#get-response")) == Pretty:
            async with aiohttp.ClientSession(headers=headers, cookies=cookies, auth=basic_auth) as session:
                try:
                    method = self.url.method.lower()
                    request_data = {f: self.url[f] for f in self.url.fields}

                    async with getattr(session, method)(str(self.url), data=request_data) as response:
                        if "json" in response.content_type:
                            data = await response.json()
                        else:
                            data = await response.text()
                            data = data.replace("\\n", "\n").replace("\\t", "\t")
                        output.update(data)
                except Exception as e:
                    output.update({"exception": type(e), "message": str(e), "dict": e.__dict__})

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        match event.state:
            case WorkerState.RUNNING:
                if self.loadingCount == 0:
                    self.query_one("#loader").mount(Loader())
                self.loadingCount += 1

                if event.worker.name == "get_url":
                    self.query_one("#get-url").disabled = True
            case WorkerState.SUCCESS:
                self.loadingCount -= 1
                if self.loadingCount == 0:
                    self.query_one("#loader").remove_children()

                    if event.worker.name == "get_url":
                        self.query_one("#get-url").disabled = False
