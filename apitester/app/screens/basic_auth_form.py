# Standard Library
from typing import Any

# Third Party
from pydantic import BaseModel, ConfigDict

# First Party
from apitester.auth import auth

# Locals
from .modal_form import ModalFormScreen


class BasicAuth(BaseModel):
    model_config = ConfigDict(title="Basic Auth")

    username: str
    password: str

    remember: bool = True


class BasicAuthScreen(ModalFormScreen[BasicAuth]):
    model = BasicAuth


    @property
    def inital(self) -> dict[str, Any]:
        return {"username": auth.username, "password": auth.password}

    def on_submit(self, model: BasicAuth) -> None:
        if model.remember:
            auth.store(model.username, model.password)
        else:
            auth.remove()

        auth["username"] = model.username
        auth["password"] = model.password

        self.notify("Basic Auth Set", title="Auth")
