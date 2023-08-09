# Standard Library
from contextlib import suppress

# Third Party
import aiohttp
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, Pretty, Static

# First Party
from apitester.auth import auth
from apitester.config import config
from apitester.data import DataStore
from apitester.url import URL
from apitester.widgets.labels import AdvancedLabel
from apitester.widgets.loader import Loader


class Endpoint(Static):
    def __init__(self, url: URL, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.url = url
        self.store = DataStore(f"{url.url}-{url.method}")

    def compose(self) -> ComposeResult:
        self.styles.padding = 1
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
                event.button.disabled = True

                with Loader() as loader:
                    self.query_one("#loader").mount(loader)
                    await self.get_url()

                event.button.disabled = False

    @on(Input.Changed)
    def update_vars(self, event: Input.Changed) -> None:
        if type(self.url) is URL:
            for field in self.url.variables():
                id = f"{field}-input"
                if type(input := self.query_one(f"#{id}")) == Input:
                    self.url[field] = input.value
                    self.store[id] = input.value

            if type(label := self.query_one("#url-label")) == Label:
                label.update(str(self.url))

    async def get_url(self):
        headers = {"accept": "application/json"}

        with suppress(KeyError):
            match config.auth.type:
                case "bearer":
                    headers["Authorization"] = f"Bearer {auth['token']}"
                case "header":
                    headers[getattr(config.auth, "key")] = auth["api_key"]

        if type(output := self.query_one("#get-response")) == Pretty:
            async with aiohttp.ClientSession(headers=headers) as session:
                try:
                    method = self.url.method.lower()
                    data = {f: self.url[f] for f in self.url.fields}

                    async with getattr(session, method)(str(self.url), data=data) as response:
                        if "json" in response.content_type:
                            data = await response.json()
                        else:
                            data = await response.text()
                            data = data.replace("\\n", "\n").replace("\\t", "\t")
                        output.update(data)
                except Exception as e:
                    output.update({"exception": type(e), "message": str(e), "dict": e.__dict__})
