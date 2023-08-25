# Standard Library

# Standard Library
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

    def __init__(self, auth: BearerAuthConf, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.auth = auth

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
                auth["token"] = extract(json, self.auth.token_path)

        self.notify("Logged in ok", title="Auth")
