# Standard Library

# Standard Library
from collections.abc import Callable
from typing import Any

# Third Party
import aiohttp
from pydantic import BaseModel, ConfigDict
from textual.widgets import Input

# First Party
from apitester.auth import auth
from apitester.config import BearerAuthConf
from apitester.utils import extract

# Locals
from .modal_form import ModalFormScreen


class LoginModel(BaseModel):
    model_config = ConfigDict(title="Login")

    username: str
    password: str
    remember: bool = True


class LoginScreen(ModalFormScreen[LoginModel]):
    model = LoginModel
    _callback = None | Callable[[str], None]

    def __init__(self, auth: BearerAuthConf, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.auth = auth

    @classmethod
    def on_got_token(cls, callback: Callable[[str], None]):
        cls._callback = callback

    def on_mount(self):
        for input in self.query("Input"):
            if type(input) is Input and input.value == "":
                input.focus()
                break
        else:
            self.query_one("#submit").focus()

    @property
    def inital(self) -> dict[str, Any]:
        return {"username": auth.username, "password": auth.password}

    async def on_submit(self, model: LoginModel) -> None:
        if model.remember:
            auth.store(model.username, model.password)
        else:
            auth.remove()

        async with aiohttp.ClientSession() as session:
            post_data = {
                "username": model.username,
                "password": model.password,
            }
            async with session.post(self.auth.url, data={**post_data}) as response:
                json = await response.json()
                token = extract(json, self.auth.token_path)
                auth["token"] = extract(json, self.auth.token_path)
                if self._callback is not None:
                    self._callback(token)

        self.notify("Logged in ok", title="Auth")
